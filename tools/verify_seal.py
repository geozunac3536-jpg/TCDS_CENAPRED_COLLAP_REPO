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
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Uso:")
        print("  python3 verify_seal.py <archivo> <archivo.sha256 | HASH>")
        print("")
        print("Ejemplos:")
        print("  python3 verify_seal.py result.json result.json.sha256")
        print("  python3 verify_seal.py result.json d2c7a0f4...")
        sys.exit(0)

    file_path = Path(sys.argv[1])

    if not file_path.exists():
        print(f"ERROR: El archivo no existe: {file_path}")
        sys.exit(1)

    expected = None

    if len(sys.argv) >= 3:
        second = Path(sys.argv[2])
        if second.exists():
            expected = second.read_text(encoding="utf-8").strip()
        else:
            expected = sys.argv[2].strip()

    if not expected:
        print("ERROR: No se proporcionó un hash o archivo .sha256")
        sys.exit(1)

    computed = sha256_file(file_path)

    print("Archivo :", file_path.name)
    print("Esperado:", expected)
    print("Calculado:", computed)

    if computed == expected:
        print("RESULTADO: OK — INTEGRIDAD VERIFICADA")
        sys.exit(0)
    else:
        print("RESULTADO: FAIL — ARCHIVO MODIFICADO")
        sys.exit(2)

if __name__ == "__main__":
    main()
