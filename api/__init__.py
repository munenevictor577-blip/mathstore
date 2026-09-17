"""Top-level api package alias forwarding to mathstore.api."""

from mathstore.api.main import app, create_app, run

__all__ = ["app", "create_app", "run"]
