"""Vercel function: POST /api/analyze."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from webapp.app import endpoint_app  # noqa: E402

app = endpoint_app("analyze")
