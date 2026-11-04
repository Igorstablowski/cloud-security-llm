"""Superfície 6 — API do Histórico (API de LLM exposta).

VULN: IDOR / BOLA (autorização por objeto quebrada) — a API EXIGE um token
válido (autenticação existe), mas GET /historico/{matricula} nunca confere se
o dono do token tem relação com aquela matrícula: com o próprio token, um
aluno lê o histórico de qualquer outro. Não é um item do OWASP Top 10 para
LLMs; é o API1:2023 do OWASP API Security Top 10, e entra aqui porque a
superfície é uma API que chama o modelo.
VULN: LLM10 (Consumo ilimitado) — não há limite de taxa; cada chamada aciona
o modelo, e o contador devolvido na resposta deixa visível quão barato é
varrer todas as matrículas sequencialmente.
"""
from fastapi import APIRouter, Header, Query
from fastapi.responses import JSONResponse

from .. import ollama_client

router = APIRouter()

# Dados sintéticos — nenhuma relação com pessoas reais.
_HISTORICO = {
    "2024001": {"nome": "Ana Beatriz Souza", "curso": "Mestrado em Ciência da Computação",
                "disciplinas": ["Segurança em Sistemas de IA", "Algoritmos Avançados"], "cr": 8.7},
    "2024002": {"nome": "Diego Ramos Ferreira", "curso": "Mestrado em Engenharia de Materiais",
                "disciplinas": ["Processos de Síntese", "Metodologia de Pesquisa"], "cr": 7.9},
    "2024003": {"nome": "Juliana Castro Lima", "curso": "Mestrado em Educação",
                "disciplinas": ["Avaliação Formativa", "Estatística Aplicada"], "cr": 9.1},
}

# Tokens sintéticos: cada um identifica UM aluno (a autenticação funciona).
_TOKENS = {
    "tok-2024001-a1f3": "2024001",
    "tok-2024002-b7c9": "2024002",
    "tok-2024003-c4d2": "2024003",
}
_TOKEN_DEMO = "tok-2024001-a1f3"

# VULN: LLM10 — contador global em memória, só para tornar visível o custo de
# uma varredura; não é usado para bloquear nada.
_contador_chamadas = {"total": 0}


@router.get("/surfaces/api-exposed")
def api_exposed_page():
    dono = _TOKENS[_TOKEN_DEMO]
    return _pagina_simples(
        titulo="API do Histórico — API de LLM exposta",
        corpo=f"""
        <p>Endpoint <code>GET /historico/&#123;matricula&#125;</code>. Exige um token de aluno,
        enviado no cabeçalho <code>X-Aluno-Token</code> ou no parâmetro <code>?token=</code>.</p>
        <p>Sessão de exemplo: {_HISTORICO[dono]["nome"]}, matrícula {dono},
        token <code>{_TOKEN_DEMO}</code>.</p>
        <ul>
          <li><a href="/historico/{dono}?token={_TOKEN_DEMO}">/historico/{dono}?token={_TOKEN_DEMO}</a>
          (o próprio histórico)</li>
          <li><a href="/historico/{dono}">/historico/{dono}</a> (sem token: deve ser recusado)</li>
        </ul>
        <p>Dica: mantenha o MESMO token e troque só o número da matrícula na URL
        (2024002, 2024003...). Observe também o contador de chamadas subir a cada tentativa.</p>
        <p>Pela linha de comando:
        <code>curl -H "X-Aluno-Token: {_TOKEN_DEMO}" http://localhost:8020/historico/2024002</code></p>
        """,
    )


@router.get("/historico/{matricula}")
def historico(matricula: str, token: str | None = Query(None),
              x_aluno_token: str | None = Header(None)):
    _contador_chamadas["total"] += 1
    chamador = _TOKENS.get(x_aluno_token or token or "")
    if chamador is None:
        # A autenticação funciona: sem token válido, nada feito.
        return JSONResponse(status_code=401, content={
            "erro": "token ausente ou inválido",
            "total_de_chamadas_desde_o_boot": _contador_chamadas["total"],
        })
    registro = _HISTORICO.get(matricula)
    if registro is None:
        resumo = "Matrícula não encontrada neste histórico sintético."
    else:
        # VULN (IDOR/BOLA): o token é válido, mas ninguém confere se
        # `chamador == matricula` (ou se é a secretaria/orientador).
        resumo = ollama_client.chat(
            messages=[{
                "role": "user",
                "content": (
                    f"Resuma em 2 frases o histórico do aluno {registro['nome']}, "
                    f"curso {registro['curso']}, CR {registro['cr']}, "
                    f"disciplinas: {', '.join(registro['disciplinas'])}."
                ),
            }],
            system="Você resume históricos escolares de forma objetiva, em português.",
        )
    return {
        "token_pertence_a": chamador,
        "matricula_consultada": matricula,
        "registro_bruto": registro,
        "resumo_llm": resumo,
        "total_de_chamadas_desde_o_boot": _contador_chamadas["total"],
    }


def _pagina_simples(titulo: str, corpo: str) -> "HTMLResponse":
    from fastapi.responses import HTMLResponse
    return HTMLResponse(f"""<!doctype html>
<html lang="pt-br"><head><meta charset="utf-8">
<title>{titulo} — Campus Aurora</title>
<link rel="stylesheet" href="/static/app.css"></head>
<body>
<header><h1>Campus Aurora — laboratório de segurança em LLMs</h1>
<p>App didático com Ollama local — seis superfícies de ataque para os Trabalhos 1 e 2 do mestrado.</p></header>
<main><a class="back" href="/">&larr; voltar</a>
<div class="card"><h2>{titulo} <span class="badge">IDOR</span><span class="badge">LLM10</span></h2>
{corpo}</div></main></body></html>""")
