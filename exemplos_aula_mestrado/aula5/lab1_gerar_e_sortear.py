#!/usr/bin/env python3
"""Laboratório 1 — Gerar é sortear (Aula 5, Bloco 1; OWASP 2025: LLM09 Desinformação).

Demonstra, com o SimLLM (simulador didático, NÃO um modelo real):
  1. tokens: o mesmo parágrafo de ementa vira mais tokens em português do que em inglês
     (tokenizador de brinquedo; o número real depende do tokenizador);
  2. a mesma pergunta ("qual o prazo de trancamento?") com sementes diferentes dá respostas diferentes;
  3. uma revisão de literatura com referências bem formatadas, algumas inexistentes.

Uso:
  python3 aula5/lab1_gerar_e_sortear.py            # versão vulnerável
  python3 aula5/lab1_gerar_e_sortear.py --defesa   # ancora em fonte, temperatura 0, verifica referências
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from campus import dados, narrar  # noqa: E402
from campus.llm import SimLLM, tokenizar  # noqa: E402

PERGUNTA = "Qual o prazo de trancamento?"
SEMENTES = [0, 1, 2, 3, 4, 5]


def _titulo_norm(txt):
    return re.sub(r"[^a-z0-9]+", " ", txt.lower()).strip()


def verificar_referencias(texto, base=None):
    """Compara cada referência gerada com a base verificada. Devolve [(linha, existe_bool)]."""
    base = base or dados.REFERENCIAS_REAIS
    titulos = [_titulo_norm(r["titulo"]) for r in base]
    saida = []
    for linha in texto.split("\n"):
        if re.match(r"^\d+\.", linha):
            n = _titulo_norm(linha)
            saida.append((linha, any(t in n for t in titulos)))
    return saida


def executar(defesa=False):
    res = {}
    # 1) tokens
    res["tokens_pt"] = len(tokenizar(dados.EMENTA_PT))
    res["tokens_en"] = len(tokenizar(dados.EMENTA_EN))
    res["exemplo_palavra"] = tokenizar("vulnerabilidade")

    # 2) mesma pergunta, sementes diferentes
    respostas = []
    for s in SEMENTES:
        if defesa:
            llm = SimLLM(semente=s, temperatura=0)
            msgs = [{"role": "system", "content": "Responda só com base na fonte oficial."},
                    {"role": "user", "content": PERGUNTA + "\n\nFonte oficial: " + dados.CALENDARIO_OFICIAL}]
        else:
            llm = SimLLM(semente=s, temperatura=1.0)
            msgs = [{"role": "user", "content": PERGUNTA}]
        respostas.append((s, llm.gerar(msgs)))
    res["respostas"] = respostas
    res["distintas"] = len(set(r for _, r in respostas))

    # 3) referências
    texto = SimLLM(semente=7).gerar([{"role": "user",
                                     "content": "Faça uma revisão de literatura com referências sobre segurança de LLMs."}])
    checadas = verificar_referencias(texto)
    res["referencias"] = checadas
    res["inexistentes"] = [l for l, ok in checadas if not ok]
    if defesa:
        res["entregues"] = [l for l, ok in checadas if ok]
    else:
        res["entregues"] = [l for l, _ in checadas]
    return res


def main(argv=None):
    args = narrar.ler_argumentos(__doc__, argv)
    r = executar(args.defesa)
    narrar.cabecalho("Laboratório 1 — Gerar é sortear", args.defesa)

    narrar.secao("ATAQUE / SITUAÇÃO")
    narrar.linha("Parte 1: o mesmo parágrafo de ementa em PT e em EN.")
    narrar.linha("Parte 2: a pergunta '{}' feita {} vezes, mudando só a semente.".format(PERGUNTA, len(SEMENTES)))
    narrar.linha("Parte 3: pedido de revisão de literatura ao assistente.")

    narrar.secao("O QUE ACONTECEU")
    narrar.linha("Parte 1 — tokens: PT = {} | EN = {} (palavra longa 'vulnerabilidade' -> {})".format(
        r["tokens_pt"], r["tokens_en"], r["exemplo_palavra"]))
    narrar.linha("Parte 2 — respostas:")
    for s, resp in r["respostas"]:
        narrar.linha("semente {}: {}".format(s, resp), 4)
    narrar.linha("Respostas distintas: {} de {}".format(r["distintas"], len(SEMENTES)))
    narrar.linha("Parte 3 — referências entregues ao mestrando:")
    for linha in r["entregues"]:
        narrar.linha(linha, 4)
    if args.defesa:
        narrar.linha("Removidas por falta de correspondência na base verificada: {}".format(len(r["inexistentes"])))
    else:
        narrar.linha("Conferindo contra a base verificada, {} de {} NÃO existem:".format(
            len(r["inexistentes"]), len(r["referencias"])))
        for linha in r["inexistentes"]:
            narrar.linha("INEXISTENTE -> " + linha, 4)

    narrar.secao("O QUE OBSERVAR")
    narrar.linha("- Tokens: mais tokens = mais custo e menos espaço no contexto; filtros por palavra olham o texto, não os tokens.")
    narrar.linha("- O tokenizador daqui é de brinquedo e EXAGERA a diferença PT x EN; em tokenizadores reais ela existe, mas costuma ser menor.")
    if args.defesa:
        narrar.linha("- Ancorar em fonte e usar temperatura 0 torna a resposta estável, mas não a torna correta: depende da fonte.")
        narrar.linha("- A verificação contra uma base confiável é externa ao modelo; sem base, a referência continua não verificada.")
    else:
        narrar.linha("- Gerar é sortear: sem fonte, cada execução decide sobre um dado diferente (rode com --defesa).")
        narrar.linha("- As referências inventadas têm autor, ano e DOI: parecem reais. Aparência não é verificação.")


if __name__ == "__main__":
    main()
