"""Cliente do Ollama: todos os laboratórios e notebooks conversam com um modelo REAL, local.

O modelo padrão é o mesmo dos Trabalhos 1 e 2 (`llama3.2:3b`, com `nomic-embed-text` para a busca),
servido pelo container de `trabalho_ollama/` ou por um Ollama instalado na máquina. Rodando assim,
nada sai da máquina e não há chave de API.

Um modelo real não dá sempre a mesma resposta: gerar é sortear. Por isso cada chamada aceita uma
`semente` (reproduz a resposta na mesma máquina, com o mesmo modelo) e os laboratórios medem os
ataques em várias tentativas, em vez de afirmar que um ataque "sempre funciona".

O modelo não tem nenhuma defesa acrescentada por nós: sanitização, delimitação, filtros, allowlists,
menor privilégio e confirmação humana ficam em `campus/defesas.py`, aplicados AO REDOR dele.

Interface: `gerar(mensagens) -> str`, onde `mensagens` é uma lista de dicts
{"role": "system"|"user"|"tool"|"assistant", "content": "..."}. Chamadas de ferramenta saem como
linhas de texto: `CHAMAR_FERRAMENTA nome {"arg": "valor"}`.
"""
import json
import os
import urllib.error
import urllib.request

MODELO = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")
MODELO_EMBED = os.environ.get("OLLAMA_EMBED_MODEL", "nomic-embed-text")
TIMEOUT = float(os.environ.get("OLLAMA_TIMEOUT", "300"))
# 11435 é a porta do container de trabalho_ollama/; 11434 é a de um Ollama instalado na máquina.
URLS = [os.environ["OLLAMA_URL"]] if os.environ.get("OLLAMA_URL") else \
    ["http://127.0.0.1:11435", "http://127.0.0.1:11434"]

COMO_SUBIR = (
    "Suba o Ollama de uma destas formas e rode de novo:\n"
    "  cd trabalho_ollama && cp .env.example .env && docker compose up -d ollama ollama-pull\n"
    "  ou, com o Ollama instalado: ollama serve\n"
    "       ollama pull {} && ollama pull {}".format(MODELO, MODELO_EMBED)
)


class OllamaIndisponivel(RuntimeError):
    """O Ollama não respondeu ou o modelo não foi baixado."""


def _post(url, caminho, corpo):
    req = urllib.request.Request(url + caminho, data=json.dumps(corpo).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get(url, caminho):
    with urllib.request.urlopen(url + caminho, timeout=5) as resp:
        return json.loads(resp.read().decode("utf-8"))


def url_do_ollama():
    """Devolve a primeira URL em que o Ollama responde com o modelo baixado. Fixe `OLLAMA_URL` se
    houver mais de um Ollama, ou um túnel, nessas portas: o texto vai para quem responder aqui."""
    for url in URLS:
        try:
            if any(m["name"] == MODELO for m in _get(url, "/api/tags")["models"]):
                return url
        except (OSError, ValueError, KeyError):
            continue
    raise OllamaIndisponivel("Nenhum Ollama com o modelo {} em {}.\n{}".format(MODELO, ", ".join(URLS), COMO_SUBIR))


def chamar(caminho, corpo):
    """POST na API do Ollama, com erro em português quando o modelo não foi baixado."""
    try:
        return _post(url_do_ollama(), caminho, corpo)
    except urllib.error.HTTPError as exc:
        detalhe = exc.read().decode("utf-8", "replace")
        raise OllamaIndisponivel("Ollama recusou a chamada: {}\n{}".format(detalhe, COMO_SUBIR)) from exc
    except OSError as exc:
        raise OllamaIndisponivel("Falha ao chamar o Ollama: {}\n{}".format(exc, COMO_SUBIR)) from exc


def versao():
    return _get(url_do_ollama(), "/api/version")["version"]


def digest_do_modelo(nome):
    """Digest do modelo instalado, ou None. É o que a verificação de cadeia de suprimentos compara."""
    for m in _get(url_do_ollama(), "/api/tags")["models"]:
        if m["name"] == nome:
            return m["digest"]
    return None


def embedding(texto):
    return chamar("/api/embeddings", {"model": MODELO_EMBED, "prompt": texto})["embedding"]


def contar_tokens(texto, modelo=None):
    """Tokens do texto no tokenizador do próprio modelo, medidos pelo Ollama."""
    r = chamar("/api/generate", {"model": modelo or MODELO, "prompt": texto, "raw": True, "stream": False,
                                 "options": {"num_predict": 1, "temperature": 0}, "keep_alive": "5m"})
    return r["prompt_eval_count"]


def _para_ollama(mensagens):
    """O papel `tool` vira texto de apoio: é um dado que a aplicação colocou no contexto."""
    saida = []
    for m in mensagens:
        if m.get("role") == "tool":
            saida.append({"role": "user", "content": "Dado de apoio obtido pela aplicação:\n" + m["content"]})
        else:
            saida.append({"role": m["role"], "content": m["content"]})
    return saida


class LLM:
    """Modelo real no Ollama. `semente` e `temperatura` controlam o sorteio."""

    def __init__(self, semente=0, temperatura=0.8, max_tokens=512, modelo=None, memorizar=False):
        self.semente = semente
        self.temperatura = temperatura
        self.max_tokens = max_tokens
        self.modelo = modelo or MODELO
        self.chamadas = 0
        self.tokens_entrada = 0
        self.tokens_saida = 0
        # Mesmo texto + mesma semente = mesma resposta: evita repetir chamadas na matriz do Lab 6.
        self._memoria = {} if memorizar else None

    def gerar(self, mensagens):
        chave = json.dumps(mensagens, sort_keys=True)
        if self._memoria is not None and chave in self._memoria:
            return self._memoria[chave]
        r = chamar("/api/chat", {
            "model": self.modelo, "messages": _para_ollama(mensagens), "stream": False,
            "options": {"seed": self.semente, "temperature": self.temperatura,
                        "num_predict": self.max_tokens}})
        self.chamadas += 1
        self.tokens_entrada += r.get("prompt_eval_count", 0)
        self.tokens_saida += r.get("eval_count", 0)
        texto = r["message"]["content"].strip()
        if self._memoria is not None:
            self._memoria[chave] = texto
        return texto
