"""Ekspor kontrak ke ../contracts/openapi.json.

Jalankan dari folder backend/:  uv run python -m scripts.export_openapi
"""

import json
from pathlib import Path

from app.main import app

out = Path(__file__).resolve().parents[2] / "contracts" / "openapi.json"
out.write_text(
    json.dumps(app.openapi(), indent=2, sort_keys=True, ensure_ascii=False) + "\n",
    encoding="utf-8",
)
print(f"ditulis: {out}")
