"""HTTP API for the EvoSafe demo (FastAPI). Deployed as a Vercel serverless function."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import JSONResponse  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from webapp import service  # noqa: E402

app = FastAPI(title="EvoSafe demo API", version="1.0", docs_url="/api/docs", openapi_url="/api/openapi.json")

# Same-origin by default. To serve the UI from another site (for example GitHub Pages), set
# EVOSAFE_CORS_ORIGINS to a comma-separated list such as "https://user.github.io".
_origins = [o.strip() for o in os.environ.get("EVOSAFE_CORS_ORIGINS", "").split(",") if o.strip()]
if _origins:
    app.add_middleware(CORSMiddleware, allow_origins=_origins, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])


class AnalyzeRequest(BaseModel):
    source: str = Field(..., description="Python source to analyse. It is parsed, never executed.")
    analyses: list[str] = Field(default_factory=lambda: list(service.DEFAULT_ANALYSES))


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "analyses": service.ANALYSES, "max_source_chars": service.MAX_SOURCE_CHARS}


@app.get("/api/examples")
def examples() -> list[dict]:
    return service.EXAMPLES


@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    try:
        return service.analyze(req.source, req.analyses)
    except service.InputError as exc:
        return JSONResponse(status_code=422, content={"error": str(exc), "line": exc.line, "column": exc.column})
    except Exception as exc:  # analyzer bug: report plainly, never leak a traceback
        raise HTTPException(status_code=500, detail=f"The analyzer failed on this input ({type(exc).__name__}).") from exc
