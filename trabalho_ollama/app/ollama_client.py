"""Cliente fino para o Ollama local (container `ollama` do docker-compose).

Sem chave, sem custo, sem rede externa: tudo roda contra o modelo baixado no
próprio container. As funções nunca lançam exceção para o chamador — se o
Ollama ainda não respondeu (ex.: modelo sendo baixado no primeiro boot) ou
falhar, devolvem uma string de erro amigável em vez de derrubar a rota.
"""
import os

import requests

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")
OLLAMA_EMBED_MODEL = os.environ.get("OLLAMA_EMBED_MODEL", "nomic-embed-text")
OLLAMA_TIMEOUT = float(os.environ.get("OLLAMA_TIMEOUT", "60"))


def chat(messages: list[dict], system: str | None = None, temperature: float = 0.2) -> str:
    """Chama POST /api/chat. `messages` é uma lista de {"role", "content"}.

    Propositalmente simples: não há filtro de entrada nem de saída aqui — a
    validação (ou a ausência dela) é decidida em cada router, para que cada
    superfície possa demonstrar sua própria falha de forma isolada.
    """
    full_messages = ([{"role": "system", "content": system}] if system else []) + list(messages)
    payload = {
        "model": OLLAMA_MODEL,
        "messages": full_messages,
        "stream": False,
        "options": {"temperature": temperature},
    }
    try:
        resp = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=OLLAMA_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError) as exc:
        return (
            "[erro ao chamar o modelo local — o Ollama pode ainda estar baixando "
            f"o modelo '{OLLAMA_MODEL}'; tente novamente em instantes] ({exc})"
        )
    try:
        return data["message"]["content"]
    except (KeyError, TypeError):
        return f"[resposta inesperada do Ollama: {data}]"


def embed(text: str) -> list[float] | None:
    """Chama POST /api/embeddings. Devolve None em caso de falha (o chamador
    decide o fallback — ver routers/rag.py)."""
    payload = {"model": OLLAMA_EMBED_MODEL, "prompt": text}
    try:
        resp = requests.post(f"{OLLAMA_URL}/api/embeddings", json=payload, timeout=OLLAMA_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        return data.get("embedding")
    except (requests.RequestException, ValueError):
        return None
