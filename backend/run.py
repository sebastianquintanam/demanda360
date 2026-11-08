"""Punto de entrada. Gunicorn usa `run:app`; en desarrollo: `flask --app run run --debug`."""

from app import create_app

app = create_app()
