# Como subir o trabalho_ollama

Passo a passo para subir, verificar e derrubar o app Campus Aurora com o Ollama local. O app roda em
containers e os modelos ficam em um volume do Docker. Detalhes das seis superfícies estão em
[trabalho_ollama/README.md](trabalho_ollama/README.md).

> O app é vulnerável de propósito. Não troque o `127.0.0.1` das portas no `docker-compose.yml`,
> principalmente em rede compartilhada, como o Wi-Fi da sala.

## Pré-requisitos

- Docker com Compose: Docker Desktop **ou** Colima (macOS).
- Cerca de 2,3 GB livres para os modelos, além das imagens.
- Portas `8020` e `11435` livres. Um Ollama nativo na porta `11434` não atrapalha.

## Opção A: Colima no macOS

É o caminho testado neste repositório (Colima 0.10.3, Docker Compose 5.7.0, Apple Silicon).

**1. Instale as ferramentas (só na primeira vez):**

```bash
brew install colima docker docker-compose
```

**2. Inicie a VM.** O padrão do Colima (2 GB de memória) é pouco para o `llama3.2:3b`:

```bash
colima start --cpu 6 --memory 8 --disk 40 -d
```

Depois da primeira vez, basta `colima start`, que reaproveita essa configuração.

**3. Suba o projeto:**

```bash
cd trabalho_ollama
cp -n .env.example .env
docker-compose up --build -d
```

Com o plugin do Compose instalado, `docker compose` (com espaço) também funciona.

## Opção B: Docker Desktop

Este caminho não foi testado aqui, mas é o que os slides dos trabalhos indicam. Abra o Docker Desktop e rode:

```bash
cd trabalho_ollama
cp -n .env.example .env
docker compose up --build -d
```

## Verifique se subiu

Na primeira vez, o comando baixa as imagens e os dois modelos. Aqui, depois de o Ollama ficar
pronto, os modelos levaram cerca de 2 minutos; o tempo depende da conexão.

```bash
docker-compose ps -a
curl -s localhost:8020/health
```

| O que olhar | Resultado esperado |
|---|---|
| Serviço `ollama` | `running (healthy)` |
| Serviço `ollama-pull` | `exited (0)`, porque ele só baixa os modelos e termina |
| Serviço `app` | `running` |
| Health check | `{"status":"ok"}` |

Depois abra:

- App: http://localhost:8020
- API do Ollama (opcional, para depuração): http://localhost:11435

Para registrar as versões (pedido no Trabalho 1):

```bash
docker-compose exec ollama ollama --version
docker-compose exec ollama ollama list
```

## Derrubar

```bash
cd trabalho_ollama
docker-compose down   # para o app e mantém os modelos baixados
colima stop           # só na Opção A: desliga a VM e libera a memória
```

Para apagar também os modelos, use `docker-compose down -v`. Na próxima subida, eles serão
baixados de novo.

## Problemas comuns

**`docker: unknown command: docker compose`**
O plugin não está instalado ou aponta para um Docker Desktop removido. Use `docker-compose`, com hífen.

**`error getting credentials ... docker-credential-desktop`**
O arquivo `~/.docker/config.json` ainda tem `"credsStore": "desktop"`, sobra de um Docker Desktop
removido. As imagens são públicas, então dá para usar uma configuração temporária, sem mexer nesse
arquivo. Rode no mesmo terminal, antes do `docker-compose`:

```bash
mkdir -p /tmp/docker-colima && echo '{}' > /tmp/docker-colima/config.json
export DOCKER_CONFIG=/tmp/docker-colima
export DOCKER_HOST=unix://$HOME/.colima/default/docker.sock
```

Para resolver de vez, remova a linha `credsStore` do `~/.docker/config.json`.

**`failed to connect to the docker API`**
A VM ou o Docker Desktop não está rodando. Rode `colima start` ou abra o Docker Desktop.

**Resposta começando com `[erro ao chamar o modelo local`**
O modelo ainda está baixando ou a chamada estourou o tempo limite. Confira o serviço `ollama-pull`
e, se ele já terminou, aumente o `OLLAMA_TIMEOUT` no `.env` e rode `docker-compose up -d`.

**A demonstração do agente parou de funcionar**
As reservas ficam em memória e o cancelamento é real dentro do app. Para restaurá-las, rode
`docker-compose restart app`.
