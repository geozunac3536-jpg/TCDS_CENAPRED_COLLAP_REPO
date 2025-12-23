# TCDS × CENAPRED — DataBridge Colaborativo (Paquete Mínimo Auditable)

Repositorio mínimo para **colaboración por paquetes de datos sellados**:

- ejecución **local** (sin exponer infraestructura),
- **recibo auditable** por entrega,
- **hash chaining** (ledger append-only),
- opción de sellado `SHA256SUMS` y firma externa.

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python ingest/verify.py --packet data/samples/sample_packet.json
python ingest/ingest.py  --packet data/samples/sample_packet.json --store data/incoming
python tools/make_seal.py --dir data/incoming --out SHA256SUMS
python tools/verify_seal.py --sums SHA256SUMS
```
