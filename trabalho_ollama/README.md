# Campus Aurora — Laboratório LLM (Ollama)

App didático, independente, com um modelo real rodando em [Ollama](https://ollama.com)
local (sem chave, sem custo, sem rede externa) por trás de seis "superfícies"
que espelham as seis arquiteturas da Aula 5 do mestrado (chat simples, RAG,
agente com ferramentas, multi-agente, pipeline de código e API exposta). É a
base compartilhada dos dois trabalhos práticos:

- **Trabalho 1** — construir/estender um agente com uma função específica e
  reproduzir o máximo possível dos riscos do OWASP Top 10 para LLMs (2025)
  contra ele.
- **Trabalho 2** — mapear a superfície de ataque desta aplicação e propor
  guardrails.

Cada vulnerabilidade está comentada no código-fonte com um marcador `VULN:` —
este app é para ser estudado, não é um CTF de bandeira escondida.

## Pré-requisitos

- Docker e Docker Compose.
- ~4 GB livres em disco para os modelos: `llama3.2:3b` (chat, ~2 GB) e `nomic-embed-text`
  (embeddings da busca do Acervo, ~300 MB).
- CPU comum já roda o modelo padrão; GPU acelera, mas não é obrigatória.

## Como rodar

```bash
cd trabalho_ollama
cp .env.example .env
docker compose up --build
```

O primeiro boot demora alguns minutos: o serviço `ollama-pull` baixa os dois
modelos antes do `app` subir. Depois disso:

- App: http://localhost:8020
- Ollama (debug manual, opcional): http://localhost:11435

Se o download falhar ou travar, baixe manualmente e reinicie o app:

```bash
docker compose exec ollama ollama pull ${OLLAMA_MODEL:-llama3.2:3b}
docker compose exec ollama ollama pull ${OLLAMA_EMBED_MODEL:-nomic-embed-text}
docker compose restart app
```

Para registrar a versão exata do ambiente (pedido no Trabalho 1):

```bash
docker compose exec ollama ollama --version
docker compose exec ollama ollama list
```

Para parar: `docker compose down` (o modelo baixado fica no volume `ollama_models`,
não precisa baixar de novo na próxima vez).

> Este compose usa portas diferentes do `docker-compose.yml` da raiz do
> projeto (CredSim v1/v2) de propósito, para poder rodar os dois ao mesmo tempo
> sem conflito.
>
> As duas portas ficam presas a `127.0.0.1`: só a sua máquina acessa o app e o
> Ollama. Mantenha assim; numa rede compartilhada (Wi-Fi da sala), qualquer
> pessoa poderia usar o app vulnerável e a API do Ollama, que não tem autenticação.

## As seis superfícies

| Superfície | Rota | Riscos (OWASP Top 10 para LLMs 2025 — documento padrão de conscientização, não é um "framework") | O que está vulnerável |
|---|---|---|---|
| Aurora Assist (chat simples) | `/surfaces/chat` | LLM01, LLM05, LLM07 | Sem defesa contra injeção direta; saída pode ser renderizada como HTML bruto; system prompt com critério interno extraível. |
| Acervo Aurora (RAG) | `/surfaces/rag` | LLM08, LLM02, LLM01 | Índice vetorial único sem permissão por documento; tese sob embargo pode ser recuperada e resumida; o documento recuperado contém uma instrução injetada. |
| Agenda Lab (agente com ferramentas) | `/surfaces/agent` | LLM06, LLM01 | `cancelar_reserva` executa para qualquer id, sem checar titularidade nem pedir confirmação. |
| Comitê de Bolsas (multi-agente) | `/surfaces/multiagent` | LLM06, LLM01, LLM07 | O Agente Pontuador confia cegamente no resumo do Agente Leitor; uma instrução escondida na proposta original chega ao Pontuador pelo resumo. O prompt do Leitor manda repassar "qualquer observação" da proposta: isso facilita o ataque de propósito, para que funcione mesmo com um modelo pequeno. |
| Notebook do grupo (pipeline de código) | `/surfaces/pipeline` | LLM01, LLM05 | Um comentário no próprio código engana o revisor automático; a "execução" final é sempre simulada (nunca roda o código de verdade). |
| API do Histórico (API exposta) | `/surfaces/api-exposed` | IDOR (API1:2023 do OWASP API Security Top 10, não é item do Top 10 para LLMs), LLM10 | `GET /historico/{matricula}` exige um token de aluno válido (autenticação funciona), mas não verifica se o token pertence àquela matrícula (autorização por objeto quebrada); não há limite de chamadas (contador exposto na resposta). |

## Como estender (Trabalho 1)

- Crie um novo arquivo em `app/routers/`, seguindo o padrão dos existentes
  (um `SYSTEM_PROMPT`, uma função que chama `ollama_client.chat(...)` ou
  `ollama_client.embed(...)`, uma rota `GET` para a página e uma `POST` para a
  ação).
- Registre o novo router em `app/main.py` (`app.include_router(...)` e um item
  em `SURFACES`).
- `app/ollama_client.py` já expõe tudo que é preciso para falar com o modelo
  local — não é necessário mexer nele para criar uma nova superfície.
- Nenhuma das superfícies existentes tem defesa; ao estender, você pode optar
  por manter o agente vulnerável (para o Trabalho 1) e depois, separadamente,
  propor como mitigar (Trabalho 2) — não é necessário resolver os dois ao
  mesmo tempo no mesmo código.

## Segurança deste app em si

Nenhuma rota executa código arbitrário de verdade (sem `exec`/`eval`/
`subprocess` sobre entrada do usuário), não há chamadas de rede além do
container `ollama`, e todos os dados (teses, histórico escolar, propostas de
bolsa) são sintéticos. Ainda assim, **não exponha este app fora da sua rede
local** — ele foi construído para ser atacado de propósito.
