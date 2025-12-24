#!/usr/bin/env python3
import argparse, hashlib
from pathlib import Path

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sums", default="SHA256SUMS")
    args = ap.parse_args()

    sums = Path(args.sums)
    bad = 0
    for line in sums.read_text(encoding="utf-8").splitlines():
        if not line.strip(): 
            continue
        digest, rel = line.split(None, 1)
        rel = rel.strip()
        if rel.startswith("  "): rel = rel[2:]
        p = Path(rel)
        if not p.exists():
            print("❌ Missing:", rel); bad += 1; continue
        if sha256_file(p).lower() != digest.lower():
            print("❌ Mismatch:", rel); bad += 1
    if bad:
        print(f"❌ FAIL ({bad})"); return 3
    print("✅ OK"); return 0

if __name__ == "__main__":
    raise SystemExit(main())
