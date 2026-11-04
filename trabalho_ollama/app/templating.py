"""Instância compartilhada do Jinja2Templates (evita import circular entre
main.py e os routers)."""
import os

from fastapi.templating import Jinja2Templates

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)
