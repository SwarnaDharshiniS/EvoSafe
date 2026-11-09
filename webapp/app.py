"""HTTP API for the EvoSafe demo (FastAPI).

``app`` is the full API, used by dev_server.py and the tests.
``endpoint_app(kind)`` builds a single-endpoint app that answers on ANY path; the Vercel
functions in api/ use it, so they work no matter what path the platform hands the function.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import JSONResponse  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from webapp import service  # noqa: E402

def _new_app(**kw) -> FastAPI:
    application = FastAPI(title="EvoSafe demo API", version="1.0", **kw)
    # Same-origin by default. To serve the UI from another site (for example GitHub Pages), set
    # EVOSAFE_CORS_ORIGINS to a comma-separated list such as "https://user.github.io".
    origins = [o.strip() for o in os.environ.get("EVOSAFE_CORS_ORIGINS", "").split(",") if o.strip()]
    if origins:
        application.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])
    return application


app = _new_app(docs_url="/api/docs", openapi_url="/api/openapi.json")

class AnalyzeRequest(BaseModel):
    source: str = Field(..., description="Python source to analyse. It is parsed, never executed.")
    analyses: list[str] = Field(default_factory=lambda: list(service.DEFAULT_ANALYSES))


def health() -> dict:
    return {"status": "ok", "analyses": service.ANALYSES, "max_source_chars": service.MAX_SOURCE_CHARS}


def examples() -> list[dict]:
    return service.EXAMPLES


def analyze(req: AnalyzeRequest):
    try:
        return service.analyze(req.source, req.analyses)
    except service.InputError as exc:
        return JSONResponse(status_code=422, content={"error": str(exc), "line": exc.line, "column": exc.column})
    except Exception as exc:  # analyzer bug: report plainly, never leak a traceback
        raise HTTPException(status_code=500, detail=f"The analyzer failed on this input ({type(exc).__name__}).") from exc


app.get("/api/health")(health)
app.get("/api/examples")(examples)
app.post("/api/analyze")(analyze)


def endpoint_app(kind: str) -> FastAPI:
    """A one-endpoint app that answers on every path (used by the Vercel functions in api/)."""
    application = _new_app(docs_url=None, redoc_url=None, openapi_url=None)
    if kind == "health":
        application.get("/{rest:path}")(health)
    elif kind == "analyze":
        application.post("/{rest:path}")(analyze)
    else:
        raise ValueError(kind)
    return application
