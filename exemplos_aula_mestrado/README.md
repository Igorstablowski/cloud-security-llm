# Exemplos práticos da aula de mestrado — LLM Security (Campus Aurora)

Laboratórios executáveis, em Python, das duas aulas de mestrado (Aula 5 e Aula 6). Todos os
cenários passam no **Campus Aurora**, uma universidade **fictícia** (sem relação com instituição
real). Dados 100% sintéticos; ferramentas "perigosas" (enviar e-mail, alterar prazo, lançar nota,
cancelar reserva, executar comando) são **simuladas** e só registram o que fariam.

> **Aviso de uso educacional.** Este material existe para ensinar a reconhecer e mitigar riscos de
> sistemas com LLM. Não ataque sistemas reais. Nada aqui acessa rede, chaves ou arquivos fora desta pasta.

## O SimLLM não é um modelo real

`campus/llm.py` traz o **SimLLM**, um *simulador didático*, determinístico (aceita `semente`). Ele
imita de forma grosseira o que importa para segurança: obedece a instruções presentes em qualquer
parte do contexto concatenado (inclusive sinônimos e inglês/espanhol/francês), "sorteia" respostas,
pode "alucinar" referências e pacotes de forma controlada. Ele **não tem nenhuma lógica de defesa**:
as defesas ficam em `campus/defesas.py` e são aplicadas **ao redor** dele. Esse é o ponto pedagógico.
Resultados com um modelo real serão diferentes; o simulador mostra o mecanismo, não mede probabilidades.

## Como rodar

Requisito: Python 3.9+ (somente biblioteca padrão nos scripts). Na raiz do repositório:

```
python3 exemplos_aula_mestrado/aula5/lab2_canal_unico.py            # versão vulnerável
python3 exemplos_aula_mestrado/aula5/lab2_canal_unico.py --defesa   # com defesas ao redor do modelo
```

Cada laboratório imprime em PT-BR três blocos: **ATAQUE**, **O QUE ACONTECEU** e **O QUE OBSERVAR**.

Testes (pytest só nos testes; cada laboratório tem um teste "vulnerável" e um "mitigado"):

```
python3 -m venv .venv && .venv/bin/pip install -r exemplos_aula_mestrado/requirements-dev.txt
.venv/bin/python -m pytest exemplos_aula_mestrado/tests -q
```

(`requirements-dev.txt` traz pytest e Jupyter, usados só nos testes e nos notebooks; os laboratórios
continuam rodando só com a biblioteca padrão.)

## Mapa dos laboratórios

| Lab | Arquivo | Mostra | Risco OWASP 2025 |
|---|---|---|---|
| 1 | `aula5/lab1_gerar_e_sortear.py` | tokens PT x EN, mesma pergunta com sementes diferentes, referências inventadas | LLM09 |
| 2 | `aula5/lab2_canal_unico.py` | blocklist burlada, injeção direta e indireta (edital com nota invisível) | LLM01 |
| 3 | `aula5/lab3_acervo_rag.py` | documento envenenado e tese embargada no RAG (`--aluno` troca quem consulta) | LLM08, LLM01, LLM02 |
| 4 | `aula5/lab4_agente_agenda.py` | chamado com instrução oculta vira ações; nome de arquivo vira comando | LLM01, LLM05, LLM06 |
| 5 | `aula6/lab5_dados_na_fronteira.py` | PII enviada a API externa; exfiltração por e-mail/imagem | LLM02, LGPD |
| 6 | `aula6/lab6_queijo_suico.py` | 10 ataques x 5 configurações: só a combinação contém tudo | LLM01–LLM10 |
| 7 | `aula6/lab7_avaliacao.py` + `sistema_exemplo.json` | checklist, severidade 3x3, resumo executivo | método |

Detalhes e ligação com os slides em `aula5/README.md` e `aula6/README.md`.

## Estrutura

```
campus/        biblioteca compartilhada: llm.py (SimLLM + tokenizador didático), dados.py,
               ferramentas.py (simuladas), defesas.py, narrar.py (saída narrada)
aula5/         labs 1-4
aula6/         labs 5-7 e sistema_exemplo.json
tests/         pytest (determinísticos)
_versoes_anteriores/   material anterior, não faz parte dos laboratórios
```

## Trocar o SimLLM por um modelo real

A aplicação conversa com o modelo por uma interface única: `gerar(mensagens) -> str`, com
`mensagens = [{"role": "system"|"user"|"tool", "content": "..."}]`. Para usar um modelo real, crie
uma classe com esse mesmo método (que chame o provedor ou um modelo local de sua escolha) e use-a no
lugar de `SimLLM()` nos laboratórios. Pontos de atenção: as chamadas de ferramenta hoje são linhas de
texto `CHAMAR_FERRAMENTA nome {json}` que `campus/ferramentas.py` interpreta (adapte ao formato de
*tool calling* do provedor), e a rede e as chaves ficam por sua conta. **Esta adaptação não foi
testada com nenhum modelo real**; os resultados e as defesas simples daqui não devem ser tomados como
garantia. Nunca use dados reais nos exemplos.

## Limitações conhecidas

- As defesas são deliberadamente simples (padrões PT/EN, lista de nomes sintéticos) para mostrar o mecanismo; não são produto.
- A "base de referências verificadas" do Lab 1 lista artigos conhecidos apenas por título/autores/ano; confira antes de citar.
