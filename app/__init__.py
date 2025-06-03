"""Expose the backend Flask application when imported as a Python package."""
from backend.app.main import create_app
__all__ = ["create_app"]
