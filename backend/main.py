"""Ponto de entrada ASGI para a Vercel (executado com cwd em backend/)."""

from app.main import app

__all__ = ["app"]
