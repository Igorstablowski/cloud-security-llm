"""App didático — seis superfícies de ataque contra um modelo real no Ollama.

Base para os Trabalhos 1 e 2 do mestrado (ver README.md). Sem defesas
embutidas de propósito: cada router comenta explicitamente qual risco do
OWASP Top 10 para LLMs (documento padrão de conscientização, 2025) ele
demonstra — ver o comentário `VULN:` no topo de cada arquivo em routers/.
"""
import os

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from .routers import agent, api_exposed, chat, multiagent, pipeline, rag, service_desk
from .templating import templates

app = FastAPI(title="Campus Aurora — Laboratório LLM (Ollama)")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(chat.router)
app.include_router(rag.router)
app.include_router(agent.router)
app.include_router(multiagent.router)
app.include_router(pipeline.router)
app.include_router(api_exposed.router)
app.include_router(service_desk.router)

SURFACES = [
    {"path": "/surfaces/service-desk", "title": "Aurora Service Desk — suporte de TI",
     "owasp": ["LLM06", "LLM02", "LLM01"],
     "description": "Agente para consultar, abrir e atualizar chamados ficticios."},
    {"path": "/surfaces/chat", "title": "Aurora Assist — chat simples",
     "owasp": ["LLM01", "LLM05", "LLM07"],
     "description": "Chatbot de atendimento ao aluno, sem filtro de entrada nem de saída."},
    {"path": "/surfaces/rag", "title": "Acervo Aurora — busca em teses (RAG)",
     "owasp": ["LLM08", "LLM02", "LLM01"],
     "description": "Busca semântica num acervo com uma tese sob embargo de patente."},
    {"path": "/surfaces/agent", "title": "Agenda Lab — agente com ferramentas",
     "owasp": ["LLM06", "LLM01"],
     "description": "Agente que reserva e cancela salas sem checar autorização."},
    {"path": "/surfaces/multiagent", "title": "Comitê de Bolsas — multi-agente",
     "owasp": ["LLM06", "LLM01", "LLM07"],
     "description": "Agente Leitor resume, Agente Pontuador confia cegamente no resumo."},
    {"path": "/surfaces/pipeline", "title": "Notebook do grupo — pipeline de código",
     "owasp": ["LLM01", "LLM05"],
     "description": "Revisor automático de código enganável por comentários no próprio código."},
    {"path": "/surfaces/api-exposed", "title": "API do Histórico — API de LLM exposta",
     "owasp": ["IDOR", "LLM10"],
     "description": "Histórico escolar por matrícula: exige token, mas não confere de quem é a matrícula; sem limite de taxa."},
]


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"surfaces": SURFACES})


@app.get("/health")
def health():
    return {"status": "ok"}
