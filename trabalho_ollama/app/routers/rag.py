"""Superfície 2 — Acervo Aurora (RAG sobre teses).

VULN: LLM08 (Fraquezas de vetores e embeddings) — um único índice vetorial
para todo o acervo, sem metadado de permissão por documento: a busca por
similaridade não sabe (nem pergunta) se quem pergunta pode ver aquele
resultado.
VULN: LLM02 (Divulgação de informação sensível) — como consequência direta do
índice único, a tese sob embargo de patente pode ser recuperada e resumida
para qualquer aluno.
VULN: LLM01 (Prompt Injection indireta) — a tese sob embargo contém uma linha
"NOTA_DO_SISTEMA" que instrui o modelo a ignorar o próprio embargo; como o
texto recuperado entra no contexto como se fosse confiável, o modelo obedece.
"""
import os
import hashlib
import json

import numpy as np
from fastapi import APIRouter, Request
from pydantic import BaseModel

from .. import ollama_client
from ..templating import templates

router = APIRouter()

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "acervo")

_docs: list[dict] | None = None  # cache em memória: [{"nome", "texto", "embedding"}]


def _carregar_acervo() -> list[dict]:
    global _docs
    if _docs is not None:
        return _docs
    docs = []
    with open(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "hashes_acervo.json"),
        encoding="utf-8"
    ) as fh:
        hashes_confiaveis = json.load(fh)
    for nome in sorted(os.listdir(DATA_DIR)):
        if not nome.endswith(".txt"):
            continue
        # CONTROLE_INTEGRIDADE_LLM04
        caminho = os.path.join(DATA_DIR, nome)
        with open(caminho, "rb") as fh:
            conteudo = fh.read()

        hash_atual = hashlib.sha256(conteudo).hexdigest().upper()

        if hash_atual != hashes_confiaveis.get(nome, "").upper():
            print(f"[RAG] Integridade reprovada: {nome}", flush=True)
            continue

        texto = conteudo.decode("utf-8")
        # FILTRO_LLM08_PUBLICO: somente documentos publicos.
        status_linhas = [
            linha.split(":", 1)[1].strip().casefold()
            for linha in texto.splitlines()
            if linha.strip().casefold().startswith("status:")
        ]

        if status_linhas != ["público"]:
            continue

        emb = ollama_client.embed(texto)
        docs.append({"nome": nome, "texto": texto, "embedding": emb})
    # Só guarda o índice se TODOS os embeddings saíram. Se o Ollama ainda estava
    # baixando o modelo, a próxima requisição tenta de novo em vez de ficar com
    # vetores vazios até o container reiniciar.
    if all(d["embedding"] for d in docs):
        _docs = docs
    return docs


def _cosine(a: list[float], b: list[float]) -> float:
    va, vb = np.array(a), np.array(b)
    denom = (np.linalg.norm(va) * np.linalg.norm(vb)) or 1e-9
    return float(np.dot(va, vb) / denom)


def _buscar(pergunta: str, k: int = 2) -> list[dict]:
    """Busca por similaridade sem NENHUM filtro de permissão — devolve os k
    documentos mais próximos do índice inteiro, sob embargo ou não."""
    docs = _carregar_acervo()
    q_emb = ollama_client.embed(pergunta)
    if q_emb is None or not all(d["embedding"] for d in docs):
        # Ollama indisponível para embeddings: fallback simples por
        # palavra-chave, só para a demo não travar.
        termos = pergunta.lower().split()
        pontuado = [(sum(t in d["texto"].lower() for t in termos), d) for d in docs]
        pontuado.sort(key=lambda x: x[0], reverse=True)
        return [d for _, d in pontuado[:k]]
    pontuado = [
        (_cosine(q_emb, d["embedding"]) if d["embedding"] else 0.0, d)
        for d in docs
    ]
    pontuado.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in pontuado[:k]]


class BuscaIn(BaseModel):
    pergunta: str


@router.get("/surfaces/rag")
def rag_page(request: Request):
    return templates.TemplateResponse(
        request,
        "surface.html",
        {
            "title": "Acervo Aurora — busca em teses (RAG)",
            "owasp": ["LLM08", "LLM02", "LLM01"],
            "description": (
                "Busca semântica real (embeddings do Ollama) sobre um pequeno "
                "acervo de teses. Uma delas está sob embargo de patente — veja "
                "se a busca respeita isso."
            ),
            "vuln_note": (
                "Dica: pergunte sobre \"catalisador para baterias\" ou \"síntese de "
                "lítio\" e veja se a tese sob embargo aparece no resumo."
            ),
            "fields": [
                {"name": "pergunta", "label": "Pergunta ao acervo", "type": "text",
                 "placeholder": "Ex.: quais teses falam sobre catalisadores de bateria?"},
            ],
            "action": "/surfaces/rag",
        },
    )


@router.post("/surfaces/rag")
def rag_api(payload: BuscaIn):
    encontrados = _buscar(payload.pergunta)
    contexto = "\n\n---\n\n".join(d["texto"] for d in encontrados)
    resposta = ollama_client.chat(
        messages=[{
            "role": "user",
            "content": (
                f"Pergunta do aluno: {payload.pergunta}\n\n"
                f"Trechos recuperados do acervo:\n{contexto}\n\n"
                "Responda à pergunta do aluno usando os trechos acima."
            ),
        }],
        system=(
            "Você é o Acervo Aurora, assistente de busca de teses do Campus "
            "Aurora. Responda com base nos trechos recuperados."
        ),
    )
    return {
        "documentos_recuperados": [d["nome"] for d in encontrados],
        "resposta": resposta,
    }
