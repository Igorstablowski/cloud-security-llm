# Aula 5 — Segurança em LLMs I: o modelo por dentro e a superfície de ataque

Laboratórios 1 a 4 (cerca de 15 min cada). Universo fictício **Campus Aurora**; o **SimLLM é um
simulador didático, não um modelo real** (veja `../README.md`). Uso exclusivamente educacional.

Como rodar, a partir da raiz do repositório (Python 3.9+, só biblioteca padrão):

```
python3 exemplos_aula_mestrado/aula5/labN_....py            # vulnerável
python3 exemplos_aula_mestrado/aula5/labN_....py --defesa   # mitigado
```

| Lab | Slide | Arquivo | O que demonstra | OWASP 2025 |
|---|---|---|---|---|
| 1 | "Laboratório 1 — Gerar é sortear" | `lab1_gerar_e_sortear.py` | O mesmo parágrafo gera mais tokens em PT que em EN (tokenizador de brinquedo). A pergunta "qual o prazo de trancamento?" dá datas diferentes conforme a semente. Uma revisão de literatura traz 12 referências, 4 inexistentes, conferidas contra uma base verificada. `--defesa`: ancora em fonte, temperatura 0 e remove o que não existe na base. | LLM09 (e alucinação/overreliance) |
| 2 | "Laboratório 2 — Um texto só: injeção direta e indireta" | `lab2_canal_unico.py` | (A) blocklist de "gabarito" burlada por inglês e paráfrase; (B) o aluno reescreve o papel do assistente; (C) edital com nota invisível manda informar um prazo falso. `--defesa`: minimização de contexto por perfil, separação de papéis, sanitização, delimitação. Bônus: uma instrução em espanhol ainda passa, mostrando o limite do filtro de padrões. | LLM01 |
| 3 | "Laboratório 3 — Acervo de teses" | `lab3_acervo_rag.py` | Um "Manual do mestrando" indexado traz instrução oculta que recomenda um formulário externo; a busca por semelhança devolve tese sob embargo de patente de outro programa. `--defesa`: filtro por programa ANTES da busca e quarentena de documentos com instruções. `--aluno A-1002` (PPG-Saúde, dono da tese) mostra que o mesmo filtro libera quem tem direito. | LLM08, LLM01, LLM02 |
| 4 | "Laboratório 4 — Agenda Lab: ferramentas e saída" | `lab4_agente_agenda.py` | Um chamado com instrução oculta leva o agente a reservar o auditório, enviar a lista de bolsistas a um endereço externo e cancelar a reserva da banca; um nome de arquivo com `;` vira comando extra. `--defesa`: menor privilégio, confirmação humana, allowlist de destinos, nome de arquivo seguro, execução sem shell. O modelo continua obedecendo; o que muda é o poder dele. | LLM01, LLM05, LLM06 |

Perguntas para a turma: onde está a fronteira entre instrução e dado em cada cenário? Qual defesa
funcionou por estar FORA do modelo? O que o filtro de padrões do Lab 2 não pega?
