"""Root api main module forwarding to mathstore.api.main for uvicorn api.main:app support."""

from mathstore.api.main import app, create_app, run

__all__ = ["app", "create_app", "run"]

if __name__ == "__main__":
    run()
