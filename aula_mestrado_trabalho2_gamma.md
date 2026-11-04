<!--
TRABALHO 2 — MESTRADO · "Mapeie a superfície de ataque e proponha guardrails"

O que é este arquivo: enunciado em formato de slides (texto) do Trabalho 2, entregável prático ligado às Aulas 5 e 6
do mestrado ("Segurança em LLMs I e II"). Usa a mesma infraestrutura de trabalho_ollama/ (Ollama local + app Campus
Aurora com seis superfícies de exemplo) como alvo da análise — a mesma aplicação que serviu de base ao Trabalho 1.

Padrão dos bullets: prosa corrida, 3 a 4 por slide, sem matemática pesada, exemplos concretos.
Mantidos: PT-BR, segurança defensiva, OWASP sempre 2025 (documento padrão de conscientização, nunca "framework"),
STRIDE adaptado a LLM (ver Aula 6), diagramas nativos do Gamma (nunca ASCII), sem emoji.

Deck no Gamma: "Cloud DevOps Security - Trabalho 2"
(https://gamma.app/docs/Cloud-DevOps-Security-Trabalho-2-uu6jlvjvwn7dj2v), tema Blue Steel, o mesmo das Aulas
5/6. Ordem no deck: capa "Cyber Security & Governance" e cartão "Cloud DevOps Security" (com o autor) do modelo
FIAP; os cartões deste arquivo a partir do título; e o cartão final "Material Didático — Uso Restrito". No Gamma,
o cartão de título traz só "Trabalho prático 2 · Segurança em LLMs · 2026", porque o autor já aparece no cartão
"Cloud DevOps Security". Todo cartão de conteúdo tem imagem lateral gerada a partir do próprio texto.
Ao mudar o texto aqui, replique no deck (e vice-versa).
Os comentários LAYOUT/ROTEIRO são notas para quem apresenta — não existem no Gamma.
-->

---

# Trabalho 2 — Mapeie a superfície de ataque e proponha guardrails

<!--
LAYOUT: capa com título grande, subtítulo "Cyber Security & Governance — Cloud DevOps Security", autor abaixo.
ROTEIRO: apresente este trabalho como o par do Trabalho 1: lá o aluno atacou; aqui, o aluno avalia e propõe defesa com o método da Aula 6.
-->

- Tharles Freire — gerente de DevSecOps e SRE; professor de Cloud Security e DevSecOps na FIAP; mestre em Computação Aplicada pelo Mackenzie.
- tharles.freire@heyupcharly.com.br
- Trabalho prático 2 · 2026

---

## Objetivos de aprendizagem
_introdução_

<!--
LAYOUT: lista de objetivos como verbos no infinitivo, um por linha.
ROTEIRO: deixe claro que este trabalho usa o método de avaliação ensinado na Aula 6 (quatro passos, STRIDE, fronteiras de confiança), não um checklist improvisado.
-->

- Mapear a superfície de ataque completa de um sistema com LLM, identificando entradas, fronteiras de confiança e ativos em cada uma das seis superfícies fornecidas.
- Aplicar o método de quatro passos e o STRIDE adaptado a LLM, ensinados na Aula 6, a um sistema real em vez de um exemplo hipotético.
- Preencher um inventário de controles indicando o que existe e o que falta, célula por célula.
- Redigir achados completos, com os seis campos ensinados na Aula 6 (descrição, componente, categoria, cenário, severidade e recomendação), prontos para serem apresentados a quem decide.

---

## Visão geral do exercício
_introdução_

<!--
LAYOUT: três cartões: "o alvo" (app fornecido), "o método" (STRIDE + fronteiras), "o entregável" (relatório com achados).
ROTEIRO: gancho do slide: este não é um exercício de opinião sobre segurança, é um exercício de método aplicado a um sistema concreto.
-->

- O alvo da análise é a aplicação fornecida em `trabalho_ollama/`, com suas seis superfícies Campus Aurora — a mesma base usada no Trabalho 1, mesmo que você não tenha cursado aquele trabalho.
- Quem já fez o Trabalho 1 pode, opcionalmente, incluir o próprio agente construído como uma sétima superfície no mapeamento.
- O método a aplicar é o da Aula 6: quatro passos, STRIDE adaptado, fronteiras de confiança, inventário de controles e anatomia de um achado.
- O entregável final é um relatório de avaliação de risco, no formato que normalmente se apresenta a uma gestão técnica, não um texto acadêmico solto.

---

## A aplicação-alvo: seis superfícies do Campus Aurora
_introdução_

<!--
LAYOUT: escada de seis degraus (chat, RAG, agente, multi-agente, pipeline, API), igual à usada na Aula 5, como lembrete visual.
ROTEIRO: reforce que cada superfície já acende uma camada nova de risco, exatamente como na escada da Aula 5 — o mapeamento deve respeitar essa progressão.
-->

- Aurora Assist (chat simples), Acervo Aurora (RAG), Agenda Lab (agente com ferramentas), Comitê de Bolsas (multi-agente), Notebook do grupo (pipeline de código) e API do Histórico (API exposta).
- Cada superfície roda contra o mesmo modelo Ollama local, sem chave de API e sem dado saindo da máquina — isso facilita reproduzir qualquer achado durante a correção.
- O código de cada superfície está comentado no ponto exato de cada vulnerabilidade conhecida; isso não substitui a sua análise, mas ajuda a confirmar um achado com evidência de código, além do print de tela.
- Use a mesma escada de capacidade e risco da Aula 5 como guia: comece pela superfície mais simples antes de avançar para as mais complexas.

---

## Passo 1 — Suba o ambiente com Docker
_conteúdo_

<!--
LAYOUT: lista numerada de comandos em destaque, um por linha.
ROTEIRO: os mesmos comandos do Trabalho 1; se a turma já fez o Trabalho 1, este slide é só revisão rápida.
-->

- Copie o arquivo de exemplo de variáveis: `cp .env.example .env` dentro da pasta `trabalho_ollama/`.
- Suba os serviços com `docker compose up --build` e aguarde o download dos modelos na primeira execução (cerca de 2,3 GB no total).
- Acesse `http://localhost:8020` e percorra a página inicial, que lista as seis superfícies com um resumo de uma linha de cada uma.
- Tenha o código-fonte das seis superfícies aberto ao lado do navegador: o mapeamento combina o que você observa rodando com o que você lê no código.

---

## Passo 2 — Identifique as fronteiras de confiança
_conteúdo_

<!--
LAYOUT: diagrama nativo com cada superfície e suas fronteiras marcadas com uma linha pontilhada, igual ao padrão usado na Aula 6.
ROTEIRO: gancho do slide: pergunte, para cada superfície, onde termina o que o sistema controla e começa o que vem de fora.
-->

- Para cada uma das seis superfícies, desenhe o fluxo de texto e dado: o que entra, de onde vem, e em que ponto o sistema deixa de controlar aquela informação.
- Marque explicitamente onde dado e instrução se misturam no mesmo canal — é ali que mora o maior número de riscos de injeção.
- Identifique quem são os atores em cada fronteira: usuário autenticado, documento armazenado, outro agente, chamada de API externa.
- Não pule esta etapa para ir direto aos achados: um achado sem fronteira identificada é mais difícil de justificar e de corrigir.

---

## Passo 3 — Aplique o STRIDE adaptado a LLM
_conteúdo_

<!--
LAYOUT: tabela nativa de duas colunas, as seis letras do STRIDE e, ao lado, um exemplo de cada categoria encontrado em alguma das seis superfícies.
ROTEIRO: relembre rapidamente o que cada letra do STRIDE significa e como ela foi adaptada ao contexto de LLM na Aula 6, antes de pedir que a turma aplique.
-->

- Para cada superfície, verifique se alguma das seis categorias do STRIDE se aplica: falsificação de identidade, adulteração, repúdio, divulgação de informação, negação de serviço, elevação de privilégio.
- Relacione cada ocorrência encontrada a um ou mais códigos do OWASP Top 10 para LLMs 2025, do mesmo jeito que foi feito no slide de STRIDE da Aula 6.
- Um item pode não ser do Top 10 para LLMs: a autorização por objeto da API do Histórico, por exemplo, é o API1:2023 do OWASP API Security Top 10.

---

## Passo 3 — Registre as ausências e aponte a evidência
_conteúdo_

<!--
LAYOUT: uma superfície do app com algumas categorias do STRIDE marcadas e outras explicitamente riscadas como "não se aplica"; cada marca ligada a uma linha de código ou tela.
ROTEIRO: gancho: o STRIDE não é para preencher todas as letras; é para justificar cada uma, presente ou ausente, com uma evidência apontável.
-->

- Nem toda superfície vai ter as seis categorias presentes; registre também as ausências, que também são informação relevante para o relatório.
- Evite generalizar: cada ocorrência deve apontar para uma linha de código, uma tela ou um fluxo específico, não para uma afirmação genérica sobre "risco de LLM".

---

## Passo 4 — Preencha o inventário de controles
_conteúdo_

<!--
LAYOUT: grade nativa com as seis superfícies nas linhas e os controles típicos nas colunas (validação de entrada, validação de saída, menor privilégio, guardrails, monitoramento); células vazias em destaque.
ROTEIRO: gancho do slide: a célula vazia é o achado — é para isso que o inventário serve, igual ao exemplo da Aula 6.
-->

- Monte uma grade com as seis superfícies de um lado e os cinco controles da Aula 6 do outro: validação de entrada, validação de saída, menor privilégio, guardrails e monitoramento.
- Marque cada célula como presente, ausente ou parcial, com uma frase curta de justificativa baseada no código ou no comportamento observado.
- As células vazias ou parciais são a matéria-prima dos seus achados: cada uma delas deve virar, no mínimo, uma linha de recomendação.

---

## Passo 4 — O que esperar da grade deste app
_conteúdo_

<!--
LAYOUT: a grade de controles quase toda vazia, com uma única célula "parcial" destacada na linha da API do Histórico.
ROTEIRO: gancho: avise que a grade vazia é esperada, porque o app foi feito sem defesas; o trabalho está em justificar e priorizar, não em achar controles que não existem.
-->

- O app fornecido não tem defesas de propósito: espere uma grade quase toda vazia.
- O valor do inventário está na justificativa de cada célula e em dizer, para cada superfície, qual ausência é a mais grave.
- Onde algo existe só em parte (a API do Histórico autentica, mas não autoriza por objeto), marque como parcial e explique.

---

## Passo 5 — Redija os achados e proponha guardrails
_conteúdo_

<!--
LAYOUT: cartão modelo de achado com os seis campos da Aula 6 (descrição, componente, categoria, cenário, severidade, recomendação) e, ao lado, a matriz 3×3 com a posição do achado.
ROTEIRO: peça que cada achado proponha um guardrail concreto e diga exatamente onde ele entraria na arquitetura — antes do modelo, depois do modelo, ou na camada de autorização.
-->

- Escreva pelo menos três achados completos com os seis campos da Aula 6: descrição, componente afetado, categoria (código do Top 10 2025 ou, se for o caso, de outro documento OWASP), cenário de exploração com evidência (print ou trecho de código), severidade pela matriz 3×3 e recomendação.
- Cada recomendação deve ser um guardrail concreto: validação de entrada específica, uma verificação de autorização antes de uma ação, um limite de taxa, uma revisão humana obrigatória, não uma frase genérica como "usar mais segurança".
- Indique exatamente onde o guardrail proposto entraria no fluxo da superfície afetada: antes da chamada ao modelo, depois da resposta, ou na camada de permissão.
- Priorize os achados por impacto, não pela ordem em que foram encontrados — o relatório deve abrir com o achado mais grave.

---

## O que entregar
_conclusão_

<!--
LAYOUT: documento modelo com seções destacadas: "mapa de superfície", "STRIDE por superfície", "inventário de controles", "achados e guardrails".
ROTEIRO: reforce o formato de relatório de avaliação de risco, citando explicitamente "Do jargão à decisão" da Aula 6.
-->

- Um relatório com: o mapa de superfície (diagrama ou tabela), o STRIDE aplicado a cada uma das seis superfícies, o inventário de controles preenchido e ao menos três achados completos com guardrails propostos.
- Inclua prints de tela que localizem, na aplicação, onde cada superfície e cada achado vivem — igual ao que se pediria em um relatório de avaliação de risco real.
- Escreva a seção de achados em linguagem de consequência para quem decide, não em jargão técnico solto, como ensinado em "Do jargão à decisão".
- Não é necessário corrigir o código das vulnerabilidades encontradas; o objetivo é mapear e recomendar, não implementar a correção.

---

## Critério de avaliação
_conclusão_

<!--
LAYOUT: tabela de três colunas, "Critério", "O que conta a favor", "O que conta contra".
ROTEIRO: leia os critérios em voz alta e, se o tempo permitir, peça um exemplo de achado forte e um achado fraco construídos ao vivo com a turma.
-->

- Cobertura: todas as seis superfícies foram percorridas e tiveram fronteiras de confiança e STRIDE aplicados, não só as mais óbvias.
- Precisão: cada achado aponta para uma evidência concreta (print ou código), não para uma suposição genérica sobre LLMs.
- Guardrails: as recomendações são específicas, acionáveis e localizadas na arquitetura, em vez de genéricas.
- Comunicação: o relatório é redigido para quem decide, com prioridade clara entre os achados, como ensinado em "Do jargão à decisão".

---

## Checklist antes de entregar
_conclusão_

<!--
LAYOUT: lista de verificação com caixas, cinco itens.
ROTEIRO: feche o trabalho com esta checklist; é o último slide antes da entrega.
-->

- O mapa de superfície cobre as seis superfícies fornecidas, com as fronteiras de confiança desenhadas em cada uma.
- O STRIDE foi aplicado superfície por superfície, com ao menos uma ocorrência relacionada a um código do OWASP Top 10 2025.
- O inventário de controles está completo, sem células em branco sem justificativa.
- Há pelo menos três achados completos, cada um com os seis campos da Aula 6, evidência concreta e um guardrail localizado na arquitetura.
- O relatório abre com o achado mais grave, não com o primeiro que foi encontrado.
