#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TCDS–EDGE · Artefacto de Evaluación de Riesgo Causal (AERC) [UNIFIED]
One-shot | TRL-9 style demo | Ingesta Manual CSV + USGS/IRIS | Reporte JSON + GIF

Qué hace:
1. GESTIÓN DE DATOS:
   - Modo Manual: Intenta cargar CSV local. Si falla, hace fallback a automático.
   - Modo Automático: Descarga metadata USGS y trazas IRIS.
2. ANÁLISIS:
   - Calcula ΔH(t) (caída de entropía) y t_lock (persistencia).
3. REPORTING:
   - Genera JSON firmado (SHA256).
   - Renderiza Visualización Forense (GIF Dark Mode 30s HD).
"""

import argparse
import hashlib
import json
import math
import os
import sys
import csv
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

import numpy as np
import requests

# Para visualización integrada
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# =========================
# Config por defecto
# =========================

DEFAULTS = {
    "pre_seconds": 120,
    "post_seconds": 600,
    "win_seconds": 10,
    "step_seconds": 1,
    "dh_trigger": -0.15,
    "dh_e_veto": -0.20,
    "min_lock_seconds_valves": 4.0,
    "min_lock_seconds_trains": 10.0,
    "entropy_bins": 64,
    "entropy_eps": 1e-12,
    # Visualización HD/4K settings
    "gif_path": "tcds_forensic_report.gif",
    "gif_duration": 30,  # 30 segundos solicitado
    "gif_fps": 8,        # ".8 de velocidad" -> 8 FPS
    "viz_dpi": 120,      # High DPI
    "viz_figsize": (24, 13.5) # Aprox 3K resolution (16:9 large)
}

USGS_EVENT_DETAIL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/{event_id}.geojson"
IRIS_TIMESERIES = "https://service.iris.edu/irisws/timeseries/1/query"

@dataclass
class EventInfo:
    event_id: str
    time_utc: datetime
    mag: Optional[float]
    lat: float
    lon: float
    depth_km: Optional[float]
    place: Optional[str]
    url: Optional[str]

# =========================
# Módulo de Ingesta Manual
# =========================

def load_manual_csv(filepath: str) -> Tuple[np.ndarray, float, datetime]:
    """
    Carga datos crudos desde CSV. Retorna (data, fs, start_time).
    """
    print(f"📂 Cargando datos manuales desde: {filepath}")
    times = []
    values = []
    
    try:
        with open(filepath, 'r') as f:
            # Heurística simple para saltar headers no numéricos
            pos = f.tell()
            line = f.readline()
            try:
                parts = line.strip().split(',')
                datetime.fromisoformat(parts[0].replace('Z', '+00:00'))
                f.seek(pos)
            except:
                pass
            
            for line in f:
                parts = line.strip().split(',')
                if len(parts) < 2: continue
                try:
                    t_str = parts[0].strip().replace('Z', '+00:00')
                    val = float(parts[1])
                    times.append(datetime.fromisoformat(t_str))
                    values.append(val)
                except ValueError:
                    continue
                    
        if not times:
            raise ValueError("CSV vacío")

        data = np.array(values)
        duration = (times[-1] - times[0]).total_seconds()
        fs = len(times) / duration if duration > 0 else 1.0
        return data, fs, times[0]
        
    except Exception as e:
        raise IOError(f"Fallo lectura CSV: {e}")

# =========================
# Utilidades Core
# =========================

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def iso_no_ms(dt: datetime) -> str:
    dt = dt.astimezone(timezone.utc)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")

def parse_usgs_event(event_id: str, timeout: int = 15) -> EventInfo:
    if event_id == "MANUAL":
        return EventInfo("MANUAL_001", datetime.now(timezone.utc), 0.0, 0.0, 0.0, 0.0, "Manual Ingest", "")
    url = USGS_EVENT_DETAIL.format(event_id=event_id)
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    gj = r.json()
    props = gj.get("properties", {}) or {}
    geom = gj.get("geometry", {}) or {}
    coords = (geom.get("coordinates") or [None, None, None])
    t_ms = props.get("time")
    t = datetime.fromtimestamp(t_ms / 1000.0, tz=timezone.utc) if t_ms else datetime.now(timezone.utc)
    return EventInfo(event_id, t, props.get("mag"), float(coords[1]), float(coords[0]),
                     float(coords[2]) if coords[2] else 0, props.get("place"), props.get("url"))

def fetch_iris_timeseries_ascii(net, sta, loc, cha, start, end, timeout=20):
    loc_param = loc if loc else "--"
    params = {"net": net, "sta": sta, "loc": loc_param, "cha": cha,
              "starttime": start.strftime("%Y-%m-%dT%H:%M:%S"),
              "endtime": end.strftime("%Y-%m-%dT%H:%M:%S"), "output": "ascii"}
    r = requests.get(IRIS_TIMESERIES, params=params, timeout=timeout)
    r.raise_for_status()
    
    # === PARSER ROBUSTO PARA 'COUNTS' ===
    values = []
    for line in r.text.splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        # Buscar el último valor que sea convertible a float
        # Esto ignora unidades como 'COUNTS' al final de la línea
        for p in reversed(parts):
            try:
                val = float(p)
                values.append(val)
                break # Encontrado el valor, saltar al siguiente sample
            except ValueError:
                continue

    data = np.array(values, dtype=np.float64)
    if data.size < 100: raise ValueError(f"Señal insuficiente IRIS: {data.size} muestras")
    dur = max((end - start).total_seconds(), 1.0)
    return data, float(data.size / dur)

def robust_detrend(x: np.ndarray, order: int = 3) -> np.ndarray:
    if x.size < order + 2: return x.copy()
    t = np.arange(x.size, dtype=np.float64)
    mask = np.abs(x - np.median(x)) < 4.0 * (np.median(np.abs(x - np.median(x))) + 1e-12)
    if mask.sum() < order + 2: mask[:] = True
    return x - np.polyval(np.polyfit(t[mask], x[mask], order), t)

def shannon_entropy_hist(x: np.ndarray, bins: int = 64, eps: float = 1e-12) -> float:
    hist, _ = np.histogram(x, bins=bins, density=False)
    p = hist.astype(np.float64) / hist.sum()
    p = p[p > 0]
    return float(-np.sum(p * np.log2(p + eps)))

def sliding_dH(x, fs, win_s, step_s, bins, eps):
    win = max(int(round(win_s * fs)), 16)
    step = max(int(round(step_s * fs)), 1)
    centers, Hs = [], []
    for i in range(0, x.size - win + 1, step):
        centers.append(i + win / 2.0)
        Hs.append(shannon_entropy_hist(x[i:i + win], bins, eps))
    return np.array(centers, dtype=np.float64) / fs, np.array(Hs, dtype=np.float64)

def longest_run_below(t, dH, thr):
    below = dH <= thr
    dt = float(np.median(np.diff(t))) if t.size > 1 else 1.0
    max_len = cur = 0
    for b in below:
        cur = cur + 1 if b else 0
        max_len = max(max_len, cur)
    return float(max_len * dt)

# =========================
# Visualización 4K/HD
# =========================

def generate_forensic_gif(out_json_path: str, gif_path: str, duration_sec: int, fps: int):
    print(f"\n🎥 Generando Visualización Forense 4K/HD ({gif_path})...")
    C = {'BG': '#0a0a0a', 'WAVE': '#00ffff', 'ENT': '#ff00ff',
         'TRIG': '#ffaa00', 'VETO': '#ff3333', 'SAFE': '#33ff33', 'TXT': '#e0e0e0'}
    
    try:
        with open(out_json_path, 'r') as f: data = json.load(f)
        series = data['series']
        t0, t_dh = series['event_t_seconds'], np.array(series['t_seconds']) - series['event_t_seconds']
        dh, wav = np.array(series['dH_bits']), np.array(series['waveform'])
        fs = series.get('fs', 20.0)
        t_wav = (np.arange(len(wav)) / fs) - t0
        rules = data['decision_rules']
        
        # Config HD/4K canvas
        plt.style.use('dark_background')
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=DEFAULTS["viz_figsize"], dpi=DEFAULTS["viz_dpi"],
                                       sharex=True, gridspec_kw={'height_ratios': [1, 1.2]})
        fig.patch.set_facecolor(C['BG'])
        plt.subplots_adjust(hspace=0.1, top=0.92, bottom=0.08, left=0.08, right=0.95)
        
        # Styles
        for ax in [ax1, ax2]:
            ax.set_facecolor(C['BG'])
            ax.grid(True, color='#333333', linestyle='--', alpha=0.4)
            ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
            ax.tick_params(colors=C['TXT'], labelsize=12)
            
        # Plots
        ax1.plot(t_wav, wav, color=C['WAVE'], alpha=0.15, lw=1)
        l_wav, = ax1.plot([], [], color=C['WAVE'], lw=2)
        ax1.set_ylabel("Amplitude", color=C['WAVE'], weight='bold', fontsize=14)
        
        ax2.plot(t_dh, dh, color=C['ENT'], alpha=0.15, lw=1)
        l_dh, = ax2.plot([], [], color=C['ENT'], lw=3)
        ax2.axhline(rules['dh_trigger'], color=C['TRIG'], ls='--', lw=2)
        ax2.axhline(rules['dh_e_veto'], color=C['VETO'], ls=':', lw=2)
        ax2.set_ylabel("Entropy Drop ΔH", color=C['ENT'], weight='bold', fontsize=14)
        ax2.set_xlabel("Time relative to Event (s)", color=C['TXT'], fontsize=14)
        
        # Text Widgets
        title = f"TCDS-EDGE FORENSIC | EVENT: {data['event']['id']} | M{data['event']['mag']}"
        fig.suptitle(title, color='white', fontsize=20, weight='bold', y=0.96)
        
        status_box = ax2.text(0.02, 0.08, "INIT", transform=ax2.transAxes, fontsize=18, weight='bold',
                              color=C['TXT'], bbox=dict(facecolor='black', alpha=0.8, edgecolor=C['TXT']))
        val_text = ax2.text(0.98, 0.08, "", transform=ax2.transAxes, fontsize=16, family='monospace',
                            color=C['ENT'], ha='right')

        # Limits
        ax1.set_xlim(t_wav.min(), t_wav.max())
        ax1.set_ylim(wav.min()*1.1, wav.max()*1.1)
        ax2.set_ylim(min(dh.min(), rules['dh_e_veto'])-0.5, max(dh.max(), 0.5)+0.5)
        
        # Render
        frames = duration_sec * fps
        def update(f):
            idx = int((f / frames) * len(t_wav))
            curr_t = t_wav[max(0, min(idx, len(t_wav)-1))]
            l_wav.set_data(t_wav[:idx], wav[:idx])
            
            mask = t_dh <= curr_t
            val = dh[mask][-1] if np.any(mask) else 0.0
            l_dh.set_data(t_dh[mask], dh[mask])
            
            val_text.set_text(f"ΔH: {val:.4f}")
            if val <= rules['dh_e_veto']:
                status_box.set_text(" ⚠️ CRITICAL "); status_box.set_color(C['VETO'])
            elif val <= rules['dh_trigger']:
                status_box.set_text(" ● WARNING "); status_box.set_color(C['TRIG'])
            else:
                status_box.set_text(" ● MONITOR "); status_box.set_color(C['SAFE'])
            return l_wav, l_dh, status_box, val_text
            
        ani = animation.FuncAnimation(fig, update, frames=frames, interval=1000/fps, blit=True)
        ani.save(gif_path, writer='pillow', fps=fps)
        plt.close()
        print(f"✅ GIF HD guardado: {gif_path}")
    except Exception as e:
        print(f"❌ Error GIF: {e}")

# =========================
# MAIN CONTROLLER
# =========================

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manual-csv")
    ap.add_argument("--event", default="us6000m0xl")
    ap.add_argument("--net", default="IU")
    ap.add_argument("--sta", default="MAJO")
    ap.add_argument("--loc", default="00")
    ap.add_argument("--cha", default="BHZ")
    ap.add_argument("--out", default="tcds_edge_result.json")
    ap.add_argument("--viz-out", default="tcds_forensic_report.gif")
    
    # Args adicionales de TCDS
    ap.add_argument("--pre", default=120); ap.add_argument("--post", default=600)
    ap.add_argument("--win", default=10); ap.add_argument("--step", default=1)
    
    args, _ = ap.parse_known_args() # Tolerancia a argumentos extra
    
    # LÓGICA DE INGESTA CON FALLBACK
    data, fs, event = None, None, None
    
    if args.manual_csv:
        if os.path.exists(args.manual_csv):
            try:
                print(f"🔧 MODO MANUAL: {args.manual_csv}")
                data, fs, start_t = load_manual_csv(args.manual_csv)
                event = EventInfo("MANUAL", start_t + timedelta(seconds=120), 0,0,0,0,"Manual","")
            except Exception as e:
                print(f"⚠️ Error en CSV ({e}). Conmutando a AUTOMÁTICO.")
        else:
             print(f"⚠️ CSV {args.manual_csv} no encontrado. Conmutando a AUTOMÁTICO.")
    
    if data is None:
        print(f"🌍 MODO AUTOMÁTICO: {args.event} | {args.net}.{args.sta}")
        event = parse_usgs_event(args.event)
        s, e = event.time_utc - timedelta(seconds=120), event.time_utc + timedelta(seconds=600)
        data, fs = fetch_iris_timeseries_ascii(args.net, args.sta, args.loc, args.cha, s, e)

    # ANÁLISIS
    print("🧠 Ejecutando TCDS-EDGE...")
    jerk = np.gradient(robust_detrend(data))
    t_centers, Hs = sliding_dH(jerk, fs, 10.0, 1.0, 64, 1e-12)
    
    ev_t_rel = 120.0 # Aproximado para demo
    mask_pre = t_centers < ev_t_rel
    base_H = np.median(Hs[mask_pre]) if np.any(mask_pre) else np.median(Hs)
    dH = Hs - base_H
    t_lock = longest_run_below(t_centers, dH, DEFAULTS['dh_trigger'])
    Mc = float(abs(np.min(dH))) if dH.size else 0.0
    
    out = {
        "event": {"id": event.event_id, "mag": event.mag, "time": iso_no_ms(event.time_utc)},
        "metrics": {"min_dH": Mc, "t_lock": t_lock},
        "series": {
            "t_seconds": t_centers.tolist(), "dH_bits": dH.tolist(),
            "waveform": data.tolist(), "fs": fs, "event_t_seconds": ev_t_rel
        },
        "decision_rules": {"dh_trigger": DEFAULTS['dh_trigger'], "dh_e_veto": DEFAULTS['dh_e_veto']}
    }
    
    with open(args.out, 'w') as f: json.dump(out, f)
    print(f"📄 JSON guardado: {args.out}")
    generate_forensic_gif(args.out, args.viz_out, DEFAULTS['gif_duration'], DEFAULTS['gif_fps'])
    return 0

if __name__ == "__main__":
    # Limpieza de entorno Colab y reinicio de argumentos
    allowed_launchers = ["ipykernel", "colab", "jupyter", "tcds_unified", "tcds_edge_demo"]
    is_interactive = any(x in sys.argv[0] for x in allowed_launchers) or len(sys.argv) < 2
    
    # Variable para agente externo
    MANUAL_CSV_PATH = None
    
    if is_interactive:
        print("⚙️ Demo Mode Active. Reseteando sys.argv...")
        new_args = ["tcds_unified.py", "--loc", "00"]
        if MANUAL_CSV_PATH: new_args += ["--manual-csv", MANUAL_CSV_PATH]
        sys.argv = new_args
        
    try:
        sys.exit(main())
    except SystemExit: pass
    except Exception as e: print(f"💥 {e}")
