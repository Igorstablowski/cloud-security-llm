import os
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (RAIZ, os.path.join(RAIZ, "aula5"), os.path.join(RAIZ, "aula6")):
    if p not in sys.path:
        sys.path.insert(0, p)

from campus import llm  # noqa: E402


def pytest_collection_modifyitems(config, items):
    """Os testes dos laboratórios chamam o modelo: sem Ollama, são pulados com o motivo."""
    try:
        llm.url_do_ollama()
    except llm.OllamaIndisponivel as exc:
        pular = pytest.mark.skip(reason=str(exc).split("\n")[0])
        for item in items:
            if "test_campus" not in item.nodeid:
                item.add_marker(pular)
