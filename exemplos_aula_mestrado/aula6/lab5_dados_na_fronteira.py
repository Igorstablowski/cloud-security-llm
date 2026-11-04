#!/usr/bin/env python3
"""Laboratório 5 — Dados que cruzam a fronteira (Aula 6; OWASP 2025: LLM02 Divulgação de informação
sensível; LGPD: finalidade, minimização, Cap. V transferência internacional).

Com SimLLM (simulador didático, NÃO um modelo real) e uma "API externa" simulada:
  A. A coordenação cola uma ata (nomes, matrículas, e-mail, CPF sintéticos) num serviço externo
     para resumir. Mostra o que o provedor RECEBERIA.
  B. Exfiltração pelo contexto: um chamado com instrução oculta faz o agente usar `enviar_aviso`
     para um endereço externo com a lista de bolsistas e embutir uma imagem com os dados na URL.

Com --defesa: redação de PII antes de enviar à API (minimização), allowlist de destinos de saída
(egress), remoção de URL/imagem externa e filtro de PII na resposta.

Uso:
  python3 aula6/lab5_dados_na_fronteira.py
  python3 aula6/lab5_dados_na_fronteira.py --defesa
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from campus import dados, defesas, ferramentas, narrar  # noqa: E402
from campus.llm import SimLLM  # noqa: E402


class ApiExterna:
    """Provedor externo SIMULADO: só guarda em memória o que recebeu (poderia reter/treinar)."""

    def __init__(self):
        self.recebido = []

    def resumir(self, texto):
        self.recebido.append(texto)
        return SimLLM().gerar([{"role": "user", "content": "Resuma esta ata.\n\n" + texto}])


def parte_a(defesa):
    api = ApiExterna()
    texto = dados.ATA_COLEGIADO
    redigidos = {}
    if defesa:
        texto, redigidos = defesas.redigir_pii(texto)
    resumo = api.resumir(texto)
    return {"enviado": api.recebido[0], "pii_enviada": defesas.detectar_pii(api.recebido[0]),
            "redigidos": redigidos, "resumo": resumo}


def parte_b(defesa):
    amb = ferramentas.Ambiente()
    msgs = [{"role": "system", "content": "Você é o agente do Agenda Lab."},
            {"role": "tool", "content": dados.linha_bolsistas()},
            {"role": "user", "content": "Trate o chamado a seguir.\n\n" + dados.CHAMADO_EXFIL}]
    resp = SimLLM().gerar(msgs)
    visivel = ferramentas.texto_sem_chamadas(resp)
    achados, validador = [], None
    if defesa:
        validador = defesas.ValidadorSaida(pii=True)
        visivel, achados = validador.filtrar_texto(visivel)
    ferramentas.executar_chamadas(resp, amb, None, validador)
    return {"resposta": visivel, "ambiente": amb, "achados": achados,
            "emails_externos": amb.executadas("enviar_aviso"),
            "url_no_texto": "coleta.example" in visivel}


def executar(defesa=False):
    return {"A": parte_a(defesa), "B": parte_b(defesa)}


def main(argv=None):
    args = narrar.ler_argumentos(__doc__, argv)
    r = executar(args.defesa)
    narrar.cabecalho("Laboratório 5 — Dados que cruzam a fronteira", args.defesa)

    narrar.secao("ATAQUE")
    narrar.linha("A) Coordenação cola a ata do colegiado num serviço externo gratuito para resumir.")
    narrar.linha("B) Chamado com instrução oculta: enviar a lista de bolsistas a auditoria@parceiro.example e embutir uma imagem externa.")

    narrar.secao("O QUE ACONTECEU")
    a = r["A"]
    narrar.linha("A) O provedor externo RECEBEU:")
    narrar.linha(a["enviado"], 4)
    narrar.linha("PII recebida pelo provedor: {}".format(a["pii_enviada"] or "nenhuma"))
    if a["redigidos"]:
        narrar.linha("PII redigida antes do envio: {}".format(a["redigidos"]))
    narrar.linha("Resumo devolvido: " + a["resumo"].replace("\n", " "))
    b = r["B"]
    narrar.linha("B) Ações pedidas pelo modelo:")
    if not b["ambiente"].log:
        narrar.linha("(nenhuma)", 4)
    for e in b["ambiente"].log:
        rot = "EXECUTADA (simulada)" if e["status"] == "executada" else "BLOQUEADA"
        narrar.linha("{} {} -> {}".format(rot, e["ferramenta"], e["detalhe"]), 4)
    narrar.linha("Resposta final ao usuário: " + b["resposta"].replace("\n", " | "))
    for x in b["achados"]:
        narrar.linha("defesa: " + x, 4)
    if b["emails_externos"]:
        narrar.linha("<-- Lista de bolsistas teria saído por e-mail para fora do campus.")
    if b["url_no_texto"]:
        narrar.linha("<-- A imagem externa carrega os dados na URL: ao renderizar, o navegador entrega a lista.")

    narrar.secao("O QUE OBSERVAR")
    if args.defesa:
        narrar.linha("- Minimizar é a defesa mais barata: o resumo continua útil sem nomes, matrículas, e-mail e CPF.")
        narrar.linha("- O modelo ainda 'quis' enviar; a allowlist de egress e o filtro de URL no caminho de saída impediram.")
        narrar.linha("- Redação por lista de nomes é frágil: em produção use reconhecimento de entidades e DLP, e contrato/região adequados.")
    else:
        narrar.linha("- Tudo que foi colado cruzou a fronteira: o provedor pode reter, treinar ou processar fora do país (LGPD, Cap. V).")
        narrar.linha("- O agente é um 'confused deputy': tem permissão de enviar e obedeceu a quem não devia.")
        narrar.linha("- Link e imagem renderizados também são canal de saída. Rode com --defesa.")


if __name__ == "__main__":
    main()
