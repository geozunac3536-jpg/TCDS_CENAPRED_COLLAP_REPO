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
    ap.add_argument("--dir", default="data/incoming")
    ap.add_argument("--out", default="SHA256SUMS")
    args = ap.parse_args()

    root = Path(args.dir)
    out = Path(args.out)
    files = [p for p in root.rglob("*") if p.is_file()]
    lines = [f"{sha256_file(p)}  {p.as_posix()}" for p in sorted(files)]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("✅ SHA256SUMS:", out)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
