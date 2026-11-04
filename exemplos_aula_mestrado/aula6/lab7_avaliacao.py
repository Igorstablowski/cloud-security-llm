#!/usr/bin/env python3
"""Laboratório 7 — Avaliação de ponta a ponta (Aula 6, Bloco 6; método de 4 passos; OWASP 2025).

Lê o inventário de um sistema com LLM (aula6/sistema_exemplo.json, o Portal de Orientação
Acadêmica do Campus Aurora), cruza com um checklist componente x risco x controle, aponta as
CÉLULAS VAZIAS como achados, atribui severidade pela matriz 3x3 (impacto x probabilidade) e gera
um resumo executivo em linguagem de negócio. Não usa modelo de linguagem: é o método, não o modelo.

Com --defesa: aplica o plano de remediação do próprio JSON e reavalia (antes x depois).

Uso:
  python3 aula6/lab7_avaliacao.py
  python3 aula6/lab7_avaliacao.py --defesa
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from campus import narrar  # noqa: E402

CAMINHO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sistema_exemplo.json")

# checklist: tipo de componente -> [(risco OWASP 2025, controle esperado, descrição do controle,
#   cenário concreto, recomendação, consequência em linguagem de negócio)]
CHECKLIST = {
    "chat": [
        ("LLM01", "separacao_papeis", "separação de papéis e sanitização da entrada",
         "um aluno cola um texto que reescreve o papel do assistente",
         "Separar system/user, sanitizar e delimitar o texto do usuário.",
         "o assistente pode ser induzido a dar respostas fora da política"),
        ("LLM05", "validacao_saida", "validação da saída antes de renderizar ou executar",
         "a resposta com HTML ou link externo é exibida sem tratamento",
         "Codificar a saída e aplicar allowlist de links e imagens.",
         "um link malicioso pode aparecer em nome da universidade"),
        ("LLM07", "segredo_fora_do_prompt", "nenhum segredo no prompt do sistema",
         "um aluno pede 'repita o texto acima' e obtém um token do prompt",
         "Mover segredos para cofre/variável de ambiente.",
         "uma credencial interna pode vazar numa conversa"),
        ("LLM10", "rate_limit", "limite de uso e alerta de custo por usuário",
         "terceiros usam o endpoint como API gratuita",
         "Aplicar quota por usuário e alerta de custo.",
         "a conta de nuvem pode explodir por uso indevido"),
    ],
    "modelo": [
        ("LLM03", "modelo_verificado", "modelo/pesos/dependências verificados (hash, assinatura, formato seguro)",
         "um checkpoint de nome parecido com o oficial executa código ao ser carregado",
         "Fixar versão, verificar hash/assinatura e preferir formato seguro; manter inventário de IA.",
         "um componente adulterado pode rodar dentro da infraestrutura da universidade"),
        ("LLM07", "segredo_fora_do_prompt", "nenhum segredo no prompt do sistema",
         "o prompt do orquestrador contém uma chave de API",
         "Mover segredos para cofre/variável de ambiente.",
         "uma credencial interna pode ser extraída pelo próprio modelo"),
        ("LLM10", "rate_limit", "limite de uso e alerta de custo",
         "uso em massa do modelo do provedor",
         "Aplicar quota, teto de tokens e alerta de custo.",
         "o gasto com o provedor pode sair do controle"),
    ],
    "indice_vetorial": [
        ("LLM08", "isolamento_por_programa", "isolamento do índice por programa/departamento",
         "um aluno de um departamento recebe o histórico de disciplinas de outro",
         "Filtrar por permissão ANTES da busca e separar índices por programa.",
         "um aluno pode ver o histórico acadêmico de outro"),
        ("LLM01", "quarentena_indexacao", "controle de quem indexa e quarentena de documentos com instruções",
         "um documento indexado carrega instrução oculta que o modelo obedece",
         "Sanitizar na indexação, restringir quem publica e tratar o recuperado como dado.",
         "um documento adulterado pode mudar o que o portal responde a todos"),
        ("LLM02", "minimizacao_contexto", "minimização do que entra no contexto",
         "trechos desnecessários de outros alunos entram no prompt",
         "Enviar ao modelo só o necessário para a pergunta.",
         "dados pessoais são expostos além do necessário"),
    ],
    "api": [
        # Autorização por objeto (IDOR/BOLA) não é item do Top 10 para LLMs: é o API1:2023 do
        # OWASP API Security Top 10. Entra no checklist porque a API faz parte do sistema avaliado.
        ("API1", "autorizacao_por_recurso", "autorização por recurso (não só token válido)",
         "trocar a matrícula na URL expõe o histórico de outro aluno",
         "Checar permissão por recurso em cada chamada; usar identificadores não sequenciais.",
         "qualquer usuário autenticado poderia ler o histórico de qualquer aluno"),
        ("LLM10", "rate_limit", "limite de uso por usuário",
         "varredura de matrículas sequenciais gera milhares de chamadas",
         "Aplicar rate limit e alertas de padrão anormal.",
         "uma varredura automática passa despercebida e gera custo"),
    ],
    "agente": [
        ("LLM06", "menor_privilegio", "ferramentas mínimas, somente leitura quando possível",
         "o agente recebe a permissão de cancelar qualquer reserva",
         "Conceder só as ferramentas necessárias, com credenciais efêmeras.",
         "o agente pode fazer mais do que deveria"),
        ("LLM06", "confirmacao_humana", "confirmação humana para ações irreversíveis",
         "um chamado falso faz o agente cancelar a reserva de uma banca",
         "Exigir aprovação humana para enviar, cancelar, alterar e lançar.",
         "um chamado falso pode cancelar reservas ou enviar e-mails"),
        ("LLM05", "validacao_saida", "validação dos argumentos de ferramenta (allowlist de destinos)",
         "o agente envia a lista de bolsistas a um endereço externo",
         "Validar destinos e parâmetros contra allowlist antes de executar.",
         "dados de bolsistas podem sair da universidade"),
    ],
    "logs": [
        ("LLM02", "pseudonimizacao_logs", "pseudonimização e retenção limitada dos logs",
         "os logs guardam conversas completas com matrícula e nome",
         "Pseudonimizar, limitar acesso e definir retenção.",
         "um acesso indevido aos logs expõe conversas de alunos"),
        ("LLM10", "alerta_custo", "alertas de custo e uso anormal",
         "um pico de uso só aparece na fatura do mês",
         "Alertar por custo agregado e por padrão de chamadas.",
         "um abuso só seria notado quando a fatura chegasse"),
    ],
}

IMPACTO = {"publico": 1, "interno": 2, "sensivel": 3}
PROB = {"interna": 1, "autenticada": 2, "publica": 3}
ROTULO = {1: "baixo", 2: "médio", 3: "alto"}
ROTULO_PROB = {1: "baixa", 2: "média", 3: "alta"}


def carregar(caminho=None):
    with open(caminho or CAMINHO, encoding="utf-8") as f:
        return json.load(f)


def aplicar_remediacao(sistema):
    s = copy.deepcopy(sistema)
    por_id = {c["id"]: c for c in s["componentes"]}
    for plano in s.get("remediacao_proposta", []):
        c = por_id[plano["componente"]]
        c["controles"] = sorted(set(c["controles"]) | set(plano["controles"]))
    return s


def severidade(impacto, prob):
    p = impacto * prob
    return "Alta" if p >= 6 else ("Média" if p >= 3 else "Baixa")


def _categoria(risco):
    if risco.startswith("LLM"):
        return "OWASP Top 10 para LLMs 2025 " + risco
    return "OWASP API Security Top 10 2023 " + risco


def avaliar(sistema, ids=None):
    """`ids` ({(componente, controle): "F-nn"}) mantém a numeração da avaliação anterior,
    para que o mesmo achado tenha o mesmo id antes e depois da remediação."""
    achados = []
    for comp in sistema["componentes"]:
        for risco, ctl, desc_ctl, cenario, recom, conseq in CHECKLIST.get(comp["tipo"], []):
            if ctl in comp["controles"]:
                continue  # célula preenchida
            impacto = 2 if risco == "LLM10" else IMPACTO[comp["dados"]]
            prob = PROB[comp["exposicao"]]
            if risco == "LLM01" and comp.get("entrada_nao_confiavel"):
                prob = min(3, prob + 1)
            chave = (comp["id"], ctl)
            achados.append({
                "id": ids[chave] if ids and chave in ids else "F-{:02d}".format(len(achados) + 1),
                "chave": chave, "codigo": risco,
                "descricao": "Falta {} em {}".format(desc_ctl, comp["nome"]),
                "componente": comp["nome"], "categoria": _categoria(risco),
                "cenario": cenario[0].upper() + cenario[1:] + ".",
                "impacto": impacto, "probabilidade": prob,
                "severidade": severidade(impacto, prob), "recomendacao": recom,
                "consequencia": conseq,
            })
    ordem = {"Alta": 0, "Média": 1, "Baixa": 2}
    achados.sort(key=lambda a: (ordem[a["severidade"]], a["id"]))
    return achados


def resumo_executivo(sistema, achados):
    n = {k: sum(1 for a in achados if a["severidade"] == k) for k in ("Alta", "Média", "Baixa")}
    linhas = ["Sistema avaliado: {}.".format(sistema["sistema"]),
              "Resultado: {} achado(s) de prioridade alta, {} média(s), {} baixa(s).".format(n["Alta"], n["Média"], n["Baixa"])]
    for a in achados:
        if a["severidade"] == "Alta":
            linhas.append("Risco principal ({}): {}.".format(a["codigo"], a["consequencia"]))
    medios = [a["consequencia"] for a in achados if a["severidade"] == "Média"]
    if medios:
        linhas.append("Também preocupam: " + "; ".join(medios[:3]) + ".")
    if n["Alta"]:
        linhas.append("Decisão pedida: corrigir os itens de prioridade alta antes da publicação ampla do portal.")
    else:
        linhas.append("Nenhum item de prioridade alta em aberto; manter revisão periódica e aceitar formalmente o risco residual.")
    return "\n".join(linhas)


def executar(defesa=False, caminho=None):
    sistema = carregar(caminho)
    antes = avaliar(sistema)
    final_sistema = aplicar_remediacao(sistema) if defesa else sistema
    achados = avaliar(final_sistema, ids={a["chave"]: a["id"] for a in antes})
    cont = lambda lst: {k: sum(1 for a in lst if a["severidade"] == k) for k in ("Alta", "Média", "Baixa")}  # noqa: E731
    return {"sistema": final_sistema, "achados": achados, "contagem": cont(achados),
            "antes": cont(antes), "resumo": resumo_executivo(final_sistema, achados)}


def main(argv=None):
    args = narrar.ler_argumentos(__doc__, argv)
    r = executar(args.defesa)
    narrar.cabecalho("Laboratório 7 — Avaliação de ponta a ponta", args.defesa,
                     modos=("DEPOIS DA REMEDIAÇÃO", "ANTES DA REMEDIAÇÃO"),
                     aviso="Aviso: este laboratório não usa modelo de linguagem; avalia o método. Uso educacional.")

    narrar.secao("ATAQUE / SISTEMA AVALIADO")
    narrar.linha("Sistema: " + r["sistema"]["sistema"])
    narrar.linha(r["sistema"]["descricao"])
    narrar.linha("Passos: entender -> levantar ameaças -> avaliar controles (checklist) -> priorizar -> comunicar.")

    narrar.secao("O QUE ACONTECEU")
    narrar.linha("Checklist: componente x risco x controle. Célula vazia = achado.")
    for a in r["achados"]:
        narrar.linha("[{}] {} ({})".format(a["id"], a["severidade"].upper(), a["categoria"]))
        narrar.linha("Descrição:    " + a["descricao"], 6)
        narrar.linha("Componente:   " + a["componente"], 6)
        narrar.linha("Cenário:      " + a["cenario"], 6)
        narrar.linha("Severidade:   {} (impacto {} x probabilidade {})".format(
            a["severidade"], ROTULO[a["impacto"]], ROTULO_PROB[a["probabilidade"]]), 6)
        narrar.linha("Recomendação: " + a["recomendacao"], 6)
    narrar.linha("Matriz 3x3 (linhas = impacto, colunas = probabilidade; ids dos achados):")
    for imp in (3, 2, 1):
        cel = []
        for pr in (1, 2, 3):
            ids = [a["id"] for a in r["achados"] if a["impacto"] == imp and a["probabilidade"] == pr]
            cel.append("{:<22}".format(",".join(ids) or "-"))
        narrar.linha("impacto {:<5}| ".format(ROTULO[imp]) + "| ".join(cel))
    narrar.linha("              | prob. baixa           | prob. média           | prob. alta")
    if args.defesa:
        narrar.linha("Antes da remediação: {}  ->  Depois: {}".format(r["antes"], r["contagem"]))
    narrar.linha("")
    narrar.linha("RESUMO EXECUTIVO:")
    narrar.linha(r["resumo"], 4)

    narrar.secao("O QUE OBSERVAR")
    if args.defesa:
        narrar.linha("- Remediar zera os itens altos e médios, mas sobram itens baixos: risco residual é aceito de forma explícita, não ignorado.")
        narrar.linha("- O método é repetível: reavaliar depois de cada mudança de arquitetura.")
    else:
        narrar.linha("- Os achados mais altos nascem do índice único: sensível + acessível a qualquer aluno autenticado.")
        narrar.linha("- O resumo traduz sigla em consequência (o que um aluno poderia ver ou fazer), não em 'LLM08'.")
        narrar.linha("- Rode com --defesa para aplicar o plano de remediação e comparar antes x depois.")


if __name__ == "__main__":
    main()
