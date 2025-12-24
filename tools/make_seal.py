#!/usr/bin/env python3
import hashlib
import sys
from pathlib import Path

def sha256_file(path: Path, chunk_size: int = 8192) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print("Uso:")
        print("  python3 make_seal.py <archivo>")
        print("")
        print("Genera el hash SHA256 del archivo y crea <archivo>.sha256")
        sys.exit(0)

    file_path = Path(sys.argv[1])

    if not file_path.exists():
        print(f"ERROR: El archivo no existe: {file_path}")
        sys.exit(1)

    digest = sha256_file(file_path)
    seal_path = file_path.with_suffix(file_path.suffix + ".sha256")

    seal_path.write_text(digest + "\n", encoding="utf-8")

    print("Archivo:", file_path.name)
    print("SHA256 :", digest)
    print("Sello  :", seal_path.name)

if __name__ == "__main__":
    main()
