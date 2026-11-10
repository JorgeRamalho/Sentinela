"""Entrypoint Vercel — carrega o FastAPI em backend/app sem conflito de pacote `app`."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
_BACKEND = _REPO / "backend"
_BACKEND_MAIN = _BACKEND / "app" / "main.py"


def _load_sentinela_app():
    if str(_BACKEND) not in sys.path:
        sys.path.insert(0, str(_BACKEND))
    spec = importlib.util.spec_from_file_location("sentinela_backend_main", _BACKEND_MAIN)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Não foi possível carregar {_BACKEND_MAIN}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["sentinela_backend_main"] = module
    spec.loader.exec_module(module)
    return module.app


app = _load_sentinela_app()
