# Gaia-Σ (TCDS) — Índice Operativo con acceso directo a Colab

Repositorio de evaluación técnica: artefacto ejecutable, auditable y no intrusivo.  
Enfoque: **riesgo causal previo** mediante coherencia y caída entrópica (ΔH), con sellado verificable.

---

## 🚀 Acceso directo (Colab)

> **REPO_URL (ajústalo solo si cambias owner/nombre):**  
> `https://github.com/geozunac3536-jpg/TCDS_CENAPRED_COLLAP_REPO`

### 1) Ejecutar el programa principal (AERC — one-shot)
Archivo: `code/code.py`

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](
https://colab.research.google.com/github/geozunac3536-jpg/TCDS_CENAPRED_COLLAP_REPO/blob/main/code/code.py
)

**Qué hace**
- Ingesta manual CSV (si lo proporcionas) o fallback automático (USGS/IRIS).
- Calcula series ΔH(t) + persistencia de bloqueo.
- Genera **JSON sellado (SHA256)** y un **GIF forense**.

---

### 2) Verificar sello criptográfico (integridad)
Archivo: `tools/verify_seal.py`

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](
https://colab.research.google.com/github/geozunac3536-jpg/TCDS_CENAPRED_COLLAP_REPO/blob/main/tools/verify_seal.py
)

---

### 3) Generar sello criptográfico (hash / firma local del artefacto)
Archivo: `tools/make_seal.py`

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](
https://colab.research.google.com/github/geozunac3536-jpg/TCDS_CENAPRED_COLLAP_REPO/blob/main/tools/make_seal.py
)

---

## ▶️ Ejecución rápida en Colab (recomendada)

1) Abre el botón **AERC — one-shot (code.py)**.  
2) En la primera celda, ejecuta esto para preparar el entorno:

```bash
!pip -q install -r https://raw.githubusercontent.com/geozunac3536-jpg/TCDS_CENAPRED_COLLAP_REPO/main/requirements.txt
