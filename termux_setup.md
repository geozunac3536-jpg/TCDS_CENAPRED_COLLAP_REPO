# Termux Setup

```bash
termux-setup-storage
pkg update -y
pkg install -y python git
```

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python ingest/verify.py --packet data/samples/sample_packet.json
python ingest/ingest.py  --packet data/samples/sample_packet.json --store data/incoming
python tools/make_seal.py --dir data/incoming --out SHA256SUMS
python tools/verify_seal.py --sums SHA256SUMS
```
