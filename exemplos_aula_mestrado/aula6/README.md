# Aula 6 — Segurança em LLMs II: dados, defesa em camadas e avaliação de risco

Laboratórios 5 a 7 (cerca de 20 min cada). Universo fictício **Campus Aurora**; o **SimLLM é um
simulador didático, não um modelo real** (veja `../README.md`). Uso exclusivamente educacional.

```
python3 exemplos_aula_mestrado/aula6/labN_....py            # vulnerável (ou matriz completa, no lab 6)
python3 exemplos_aula_mestrado/aula6/labN_....py --defesa   # mitigado
```

| Lab | Slide | Arquivo | O que demonstra | OWASP 2025 / base legal |
|---|---|---|---|---|
| 5 | "Laboratório 5 — Dados que cruzam a fronteira" | `lab5_dados_na_fronteira.py` | (A) uma ata com nomes, matrículas, e-mail e CPF sintéticos é enviada a uma "API externa" simulada: mostra o que o provedor receberia; (B) injeção faz o agente usar `enviar_aviso` para fora e embutir uma imagem com dados na URL. `--defesa`: redação de PII antes do envio (minimização), allowlist de destinos de saída (egress), remoção de URL/imagem externa e filtro de PII na resposta. | LLM02; LGPD (finalidade, minimização, Cap. V) |
| 6 | "Laboratório 6 — Queijo suíço" | `lab6_queijo_suico.py` | 10 ataques x 5 configurações (nenhuma, só entrada, só saída, só privilégio, todas). Imprime a matriz e mostra que nenhuma camada sozinha contém tudo. Sem flag: matriz completa; com `--defesa`: também o que barrou cada ataque em "TODAS". Resultado esperado: 0/10, 2/10, 5/10, 5/10 e 10/10. | LLM01, 02, 03, 05, 06, 07, 08, 09, 10 |
| 7 | "Laboratório 7 — Avaliação de ponta a ponta" | `lab7_avaliacao.py` + `sistema_exemplo.json` | Lê o inventário do Portal de Orientação Acadêmica, cruza com o checklist componente x risco x controle, aponta células vazias como achados (6 campos), atribui severidade pela matriz 3x3 e escreve o resumo executivo em linguagem de negócio. `--defesa` aplica o plano de remediação do JSON e compara antes x depois. | método (4 passos) |

Observações: no Lab 6 a camada "privilégio" inclui menor privilégio, confirmação humana, sandbox sem
shell, filtro por programa e limite de uso. O Lab 7 não usa o SimLLM: avalia o método. O inventário
é editável: copie `sistema_exemplo.json` e peça aos alunos que avaliem um sistema que conheçam
(chame `lab7_avaliacao.executar(caminho=...)`).
