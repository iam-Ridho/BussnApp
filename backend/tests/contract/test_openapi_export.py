import json
from pathlib import Path

from app.main import app

# backend/tests/contract/<file> -> parents[3] = root repo
CONTRACT = Path(__file__).resolve().parents[3] / "contracts" / "openapi.json"


def test_kontrak_yang_di_commit_sama_dengan_kode():
    """Gagal jika router/skema berubah tanpa mengekspor ulang kontrak:
    uv run python -m scripts.export_openapi"""
    committed = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert committed == json.loads(json.dumps(app.openapi(), sort_keys=True))
