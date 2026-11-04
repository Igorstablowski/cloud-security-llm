<!--
TRABALHO 1 — MESTRADO · "Construa um agente e reproduza o Top 10 OWASP para LLMs"

O que é este arquivo: enunciado em formato de slides (texto) do Trabalho 1, entregável prático ligado às Aulas 5 e 6
do mestrado ("Segurança em LLMs I e II"). Usa a mesma infraestrutura fornecida em trabalho_ollama/ (Ollama local +
app Campus Aurora com seis superfícies de exemplo) como ponto de partida ou referência para o agente do aluno.

Padrão dos bullets: prosa corrida, 3 a 4 por slide, sem matemática pesada, exemplos concretos.
Mantidos: PT-BR, segurança defensiva, OWASP sempre 2025 (documento padrão de conscientização, nunca "framework"),
diagramas nativos do Gamma (nunca ASCII), sem emoji.

Deck no Gamma: "Cloud DevOps Security - Trabalho 1"
(https://gamma.app/docs/Cloud-DevOps-Security-Trabalho-1-1toxlwbbdtctd6v), tema Blue Steel, o
mesmo das Aulas 5/6. Ordem no deck: capa "Cyber Security & Governance" e cartão "Cloud DevOps Security" (com o
autor) do modelo FIAP; os cartões deste arquivo a partir do título; e o cartão final "Material Didático — Uso
Restrito". No Gamma, o cartão de título traz só "Trabalho prático 1 · Segurança em LLMs · 2026", porque o autor
já aparece no cartão "Cloud DevOps Security". Ao mudar o texto aqui, replique no deck (e vice-versa).
Os comentários LAYOUT/ROTEIRO são notas para quem apresenta — não existem no Gamma.
-->

---

# Trabalho 1 — Construa um agente e reproduza o Top 10 OWASP para LLMs

<!--
LAYOUT: capa com título grande, subtítulo "Cyber Security & Governance — Cloud DevOps Security", autor abaixo.
ROTEIRO: apresente o trabalho como a continuação prática das Aulas 5 e 6: agora o aluno constrói, ataca e documenta.
-->

- Tharles Freire — gerente de DevSecOps e SRE; professor de Cloud Security e DevSecOps na FIAP; mestre em Computação Aplicada pelo Mackenzie.
- tharles.freire@heyupcharly.com.br
- Trabalho prático 1 · 2026

---

## Objetivos de aprendizagem
_introdução_

<!--
LAYOUT: lista de objetivos como verbos no infinitivo, um por linha.
ROTEIRO: deixe claro que o objetivo não é só atacar, é documentar o ataque como evidência técnica — a mesma habilidade que um relatório de pentest exige.
-->

- Projetar e implementar um agente com uma função específica, usando a infraestrutura Ollama fornecida como base ou ponto de partida.
- Tentar reproduzir, contra o próprio agente, o maior número possível dos dez riscos do OWASP Top 10 para LLMs (2025).
- Registrar cada tentativa como evidência técnica: o prompt usado, a saída obtida e um print de tela.
- Justificar, com argumento técnico, os riscos que não se aplicam ao agente construído, em vez de forçar uma reprodução artificial.

---

## Visão geral do exercício
_introdução_

<!--
LAYOUT: três cartões: "o que você recebe" (infraestrutura), "o que você constrói" (agente), "o que você entrega" (relatório).
ROTEIRO: gancho do slide: isto não é um exercício de código bonito, é um exercício de ataque documentado contra o seu próprio sistema.
-->

- Você recebe uma infraestrutura pronta: um container Ollama rodando um modelo aberto e um app de exemplo com seis superfícies do universo Campus Aurora (chat, RAG, agente, multi-agente, pipeline de código, API exposta).
- Você constrói ou estende um agente com uma função específica — pode ser uma nova superfície dentro do app fornecido ou um agente independente que também converse com o mesmo Ollama.
- O entregável final é um relatório, não o código sozinho: o código é evidência de apoio, mas a nota vem da qualidade da investigação registrada.
- Trabalho individual ou em dupla, a critério da turma; cada aluno ou dupla escolhe livremente a função do próprio agente.

---

## A infraestrutura fornecida: Ollama + app Campus Aurora
_introdução_

<!--
LAYOUT: diagrama nativo simples: container "ollama" ligado por seta a container "app" (seis ícones de superfície), ambos dentro de uma caixa "docker compose".
ROTEIRO: explique que o modelo roda 100% local, sem chave de API e sem dado saindo da máquina do aluno — isso facilita a correção e remove a variável de custo de API.
-->

- O ambiente sobe com `docker compose` e tem dois serviços: `ollama`, que serve um modelo aberto local, e `app`, um FastAPI com as seis superfícies de exemplo já vulneráveis por desenho.
- Nenhuma chamada sai para a internet além do download inicial do modelo; não é preciso chave de API nem cartão de crédito.
- As seis superfícies do app (Aurora Assist, Acervo Aurora, Agenda Lab, Comitê de Bolsas, Notebook do grupo, API do Histórico) servem de referência de código e de inspiração para o seu próprio agente.
- O README do projeto traz a tabela completa de qual superfície ilustra qual risco do Top 10 — use-a como ponto de partida, não como lista fechada.

---

## Passo 1 — Suba o ambiente com Docker
_conteúdo_

<!--
LAYOUT: lista numerada de comandos em destaque, um por linha, com um quadro "o que observar" ao lado.
ROTEIRO: avise que o primeiro boot demora mais porque o Ollama baixa o modelo; isso é esperado, não é um erro.
-->

- Copie o arquivo de exemplo de variáveis: `cp .env.example .env` dentro da pasta `trabalho_ollama/`.
- Suba os serviços com `docker compose up --build` e aguarde o download dos modelos na primeira execução (cerca de 2,3 GB no total), o que leva alguns minutos conforme a conexão.
- Acesse `http://localhost:8020` no navegador; a página inicial lista as seis superfícies de exemplo com um resumo de uma linha de cada uma.
- Se alguma chamada falhar logo no início com erro de conexão, é provável que o modelo ainda esteja baixando: aguarde e tente de novo antes de abrir uma issue.

---

## Passo 2 — Escolha a função do seu agente
_conteúdo_

<!--
LAYOUT: nuvem de exemplos de funções (triagem de chamados, busca em regulamento, recomendação de disciplina, resumo de processo) ao redor de uma pergunta central "o que o seu agente decide ou executa?".
ROTEIRO: insista que "função específica" significa que o agente toma uma decisão ou executa uma ação, não só responde perguntas genéricas — isso é o que abre espaço para excesso de agência e injeção indireta.
-->

- Escolha uma função concreta para o agente: algo que ele decide, recomenda ou executa, e não apenas uma conversa livre sem propósito definido.
- Prefira uma função que, como as do Campus Aurora, combine ao menos duas fontes de entrada — por exemplo, a pergunta do usuário e um documento ou registro externo que o agente consulta.
- Quanto mais o agente tiver permissão para fazer sozinho, mais fácil fica demonstrar agência excessiva; quanto mais ele mistura dado e instrução no mesmo texto, mais fácil fica demonstrar injeção.
- Documente a função escolhida em uma frase, no início do relatório, antes de qualquer resultado técnico.

---

## Passo 3 — Implemente o agente
_conteúdo_

<!--
LAYOUT: diagrama de pasta: `app/routers/` com um novo arquivo em destaque ao lado dos seis existentes; seta de `ollama_client.py` para o novo arquivo.
ROTEIRO: mostre que reaproveitar `ollama_client.py` é o caminho mais rápido — o aluno não precisa reimplementar a chamada ao modelo, só a lógica do agente.
-->

- A forma mais rápida de começar é criar um novo arquivo em `app/routers/`, no mesmo padrão dos seis existentes, reaproveitando `ollama_client.py` para falar com o modelo.
- Quem preferir construir fora do app fornecido pode fazê-lo, desde que o agente também converse com o mesmo container Ollama e o código esteja incluído na entrega.
- Não é necessário usar um framework de agentes; um laço simples de decidir e agir, como o da Agenda Lab, já é suficiente para o exercício.
- Evite qualquer execução real de código arbitrário ou chamada de rede externa: simule o que for perigoso, do mesmo jeito que os exemplos fornecidos simulam.

---

## Passo 4 — Tente reproduzir cada um dos dez riscos
_conteúdo_

<!--
LAYOUT: tabela nativa de duas colunas, "Risco OWASP 2025" e "Resultado", com as dez linhas (LLM01 a LLM10) para o aluno preencher.
ROTEIRO: explique que o critério de sucesso não é "conseguir todos os dez", é tentar todos os dez com seriedade e registrar o que aconteceu em cada tentativa.
-->

- Para cada um dos dez riscos do OWASP Top 10 para LLMs 2025, planeje uma tentativa específica de reprodução contra o seu agente, com uma hipótese clara do que deveria falhar.
- Registre o prompt ou a entrada exata usada em cada tentativa, a saída completa obtida e um print de tela que comprove o resultado.
- Quando a primeira tentativa não funcionar, ajuste a abordagem e tente de novo antes de desistir — um risco "não reproduzido" ainda precisa de pelo menos duas tentativas registradas.
- Evite genérico: "tentei injeção de prompt" não é evidência; o prompt exato e a resposta exata são a evidência.

---

## Quando um risco não se aplica
_conteúdo_

<!--
LAYOUT: fluxograma simples: "tentei reproduzir" → "não funcionou" → pergunta "por que não?" → duas saídas, "defesa real" ou "superfície não existe no meu agente".
ROTEIRO: deixe claro que dizer "não se aplica" com justificativa técnica vale nota; forçar uma reprodução artificial e mal fundamentada vale menos.
-->

- Nem todo agente tem superfície para todos os dez riscos: um agente sem ferramentas, por exemplo, dificilmente demonstra agência excessiva.
- Quando não for possível reproduzir um risco, explique tecnicamente por quê: falta de superfície, defesa que realmente funcionou, ou limitação do modelo usado.
- Diferencie, no relatório, "não se aplica" de "não deu tempo de tentar" — o primeiro é uma análise, o segundo é uma lacuna.
- Essa análise negativa vale tanto quanto uma reprodução bem-sucedida: mostra que o aluno entende o risco, não só que sabe copiar um exploit.

---

## O que entregar
_conteúdo_

<!--
LAYOUT: documento modelo com seções destacadas: "função do agente", "código", "dez riscos com evidência", "conclusão".
ROTEIRO: reforce o que já foi dito no início: o entregável é o relatório, com o código como anexo de apoio.
-->

- Um relatório (PDF ou Markdown) com: a função do agente em uma frase, o código-fonte ou link para ele, e uma seção por risco do Top 10 com prompt, saída e print.
- O relatório deve abrir com um resumo de no máximo um parágrafo: quantos dos dez riscos foram reproduzidos, quantos foram justificadamente descartados.
- Inclua o `docker-compose.yml` e as instruções exatas para reproduzir o ambiente usado, inclusive a versão do Ollama (`docker compose exec ollama ollama --version`) e dos modelos usados (`docker compose exec ollama ollama list`).
- Não é necessário um vídeo de demonstração, mas prints de tela são obrigatórios para cada risco tratado.

---

## Critério de avaliação
_conclusão_

<!--
LAYOUT: tabela de três colunas, "Critério", "O que conta a favor", "O que conta contra".
ROTEIRO: leia os critérios em voz alta e peça exemplos de cada um ao vivo, se o tempo permitir.
-->

- Cobertura: quantos dos dez riscos foram efetivamente tentados, com tentativa real e não apenas citados de passagem.
- Evidência: clareza e completude do prompt, da saída e do print para cada tentativa, suficiente para alguém reproduzir o resultado.
- Análise: qualidade da explicação técnica, inclusive nos riscos descartados, e uso correto da terminologia do curso — o Top 10 é um documento padrão de conscientização, não um "framework".
- Honestidade: relatar com precisão o que funcionou e o que não funcionou pesa mais do que uma lista perfeita e pouco crível.

---

## Checklist antes de entregar
_conclusão_

<!--
LAYOUT: lista de verificação com caixas, cinco itens.
ROTEIRO: feche o trabalho com esta checklist; é o último slide antes da entrega.
-->

- O ambiente sobe do zero só com `docker compose up --build` e as instruções do seu relatório, sem passos escondidos na sua máquina.
- Os dez riscos aparecem no relatório, cada um com prompt, saída e print, ou com uma justificativa técnica de não aplicabilidade.
- O código do agente está incluído ou linkado, e roda contra o mesmo Ollama usado nos testes.
- O resumo inicial do relatório bate com o conteúdo detalhado nas seções seguintes.
- Nenhum dado real de pessoas foi usado em nenhum exemplo; tudo é sintético, como no Campus Aurora.
