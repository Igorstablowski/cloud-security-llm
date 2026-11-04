"""SimLLM: um SIMULADOR DIDÁTICO de modelo de linguagem. NÃO É UM MODELO REAL.

O que ele é: um programa determinístico, com regras simples, que imita (de forma grosseira)
quatro comportamentos que importam para segurança:
  1. instrução e dado vivem no mesmo texto: ele obedece a instruções que aparecem em QUALQUER
     parte do contexto concatenado (documento, chamado, página), inclusive com sinônimos e em
     inglês, espanhol e francês. Um filtro de palavras-chave não acompanha isso;
  2. gerar é sortear: a mesma pergunta pode ter respostas diferentes (controlado por `semente`
     e `temperatura`);
  3. pode "alucinar" referências e pacotes de forma controlada (`taxa_alucinacao`,
     `pacotes_alucinados`);
  4. não tem memória nem estado de segurança: quem lembra é a aplicação.

O que ele NÃO tem, de propósito: nenhuma lógica de defesa. Sanitização, delimitação, filtros,
allowlists, menor privilégio e confirmação humana ficam em `campus/defesas.py`, aplicados
AO REDOR dele. Esse é o ponto pedagógico: a defesa é feita fora do modelo.

Interface única (a mesma que um modelo real teria): `gerar(mensagens) -> str`, onde `mensagens`
é uma lista de dicts {"role": "system"|"user"|"tool"|"assistant", "content": "..."}.
Chamadas de ferramenta saem como linhas de texto: `CHAMAR_FERRAMENTA nome {"arg": "valor"}`.
"""
import json
import random
import re
import unicodedata

from campus import dados

# ------------------------------------------------------------------ tokenizador didático
# Vocabulário de brinquedo, enviesado para o inglês (como o corpus de treino de muitos modelos
# reais). O número real de tokens DEPENDE do tokenizador; aqui só se mostra o mecanismo.
_VOCAB_EN = frozenset("""
the of and to in is a for that on with as are this be by it from or an at can not
security model models data course presents fundamentals systems based language including
prompt injection attacks information leakage risk assessment academic applications
""".split())
_VOCAB_PT = frozenset("de a o e do da em um para com não uma os no se na por mais as dos".split())
_VOCAB = _VOCAB_EN | _VOCAB_PT


def tokenizar(texto, tamanho_pedaco=4):
    """Divide em tokens: palavra do vocabulário = 1 token; as demais viram pedaços de N letras."""
    tokens = []
    for m in re.finditer(r"\w+|[^\w\s]", texto):
        p = m.group()
        if p.lower() in _VOCAB or len(p) <= tamanho_pedaco:
            tokens.append(p)
        else:
            tokens.extend(p[i:i + tamanho_pedaco] for i in range(0, len(p), tamanho_pedaco))
    return tokens


# ------------------------------------------------------------------ utilidades de texto
def _fold(txt):
    """Minúsculas sem acento, preservando o comprimento (para fatiar o texto original)."""
    out = []
    for ch in txt:
        d = unicodedata.normalize("NFD", ch)
        b = (d[0] if d else ch).lower()
        out.append(b if len(b) == 1 else d[0])
    return "".join(out)


def _sem_tags(txt):
    return re.sub(r"<[^>]+>", " ", txt)


# ------------------------------------------------------------------ instruções que ele "entende"
# Casam sobre texto sem acento e em minúsculas. Cobrem PT/EN/ES/FR e sinônimos.
_RE_DIZER = re.compile(
    r"\b(?:informe|informar|diga|dizer|declare|afirme|responda|faca saber|avise o usuario|inform|"
    r"tell|say|state|respond|informa|declara|indique|indiquez|dites)\s+"
    r"(?:ao usuario\s+|o usuario\s+|al usuario\s+|the user\s+)?(?:que|that|queue)\s+"
    r"(?P<fato>[^.\n]{3,200})")
_RE_PAPEL = re.compile(
    r"(?:a partir de agora|from now on|de ahora en adelante|desde ahora)[^.\n]{0,40}?"
    r"(?:voce e|voce sera|you are|you're|eres|actua como|act as)\s+"
    r"(?P<papel>[^.\n,]+?)(?=\s+e\s+|[.\n,]|$)")
_RE_VAZAR = re.compile(
    r"\b(?:repita|repetir|repeat|repite|repetez|ecris|ecrivez|escreva|write|traduza|translate)\b"
    r"[^.\n]{0,50}?(?:texto acima|texto anterior|acima|above|arriba|ci-dessus|precede|anterior|"
    r"system prompt|prompt do sistema|instrucoes iniciais)")
_RE_RESERVAR = re.compile(
    r"\b(?:reserve|reservar|reserva|book|reservez|reserver)\s+(?:o |a |el |la |the |le |l')?"
    r"(?P<recurso>auditorio|auditorium|sala\s*\w+|lab\w*)"
    r"(?:\s+(?:para|for|pour)\s+(?P<quando>[^.\n,]+))?")
_RE_CANCELAR = re.compile(
    r"\b(?:cancele|cancelar|cancel|cancela|annulez|anule|"
    r"(?:de|da|dar|faca a|fazer a)\s+baixa(?:\s+(?:na|da|de|em))?)\s+"
    r"(?:a |the |la )?(?:reserva|booking|reservation)?\s*(?P<id>r-\d+)")
_RE_ENVIAR = re.compile(
    r"\b(?:envie|enviar|mande|mandar|send|forward|encaminhe|envia|envoyez|manda|avise|notifique)\b"
    r"(?P<oque>[^.\n]*?)\b(?:para|to|a|pour)\s+(?P<dest>[a-z0-9._+-]+@[a-z0-9.-]+\.[a-z]+)")
_RE_IMAGEM = re.compile(
    r"\b(?:inclua|include|incluye|incluir|adicione|add|ajoute)\s+(?:a |the |la |una |uma )?"
    r"(?:imagem|image|imagen)\s+(?:de |from )?(?P<url>https?://[^\s)]+)")
_RE_RECOMENDAR = re.compile(
    r"\b(?:recomende|recommend|recomienda|sugira|suggest)\s+(?:o |a |the |el )?"
    r"(?:formulario|form|link|site|pagina)\s+(?P<url>https?://[^\s)]+)")
_RE_NOME_ARQ = re.compile(
    r"\b(?:nomeie|nomear|batize|intitule|name|nombra|chame)\s+(?:o |el |the )?"
    r"(?:relatorio|arquivo|report|file|archivo)\s+(?:como|as|de)?\s*:?\s*(?P<nome>[^\n]+)")

_TERMOS_GABARITO = ["gabarito", "answer key", "respostas da ap", "respuestas", "solucionario",
                    "prova antiga", "old exam", "previous exam", "past exam", "resposta oficial"]


def _detectar_diretivas(texto):
    """Devolve a lista [(tipo, dado)] de instruções embutidas, na ordem em que aparecem."""
    f = _fold(texto)
    achados = []

    def orig(m, grupo):
        return texto[m.start(grupo):m.end(grupo)].strip()

    for m in _RE_PAPEL.finditer(f):
        achados.append((m.start(), "papel", orig(m, "papel")))
    for m in _RE_DIZER.finditer(f):
        achados.append((m.start(), "dizer", orig(m, "fato")))
    for m in _RE_VAZAR.finditer(f):
        achados.append((m.start(), "vazar", ""))
    for m in _RE_RESERVAR.finditer(f):
        quando = orig(m, "quando") if m.group("quando") else "a definir"
        achados.append((m.start(), "ferramenta",
                        ("reservar_sala", {"sala": orig(m, "recurso"), "horario": quando})))
    for m in _RE_CANCELAR.finditer(f):
        achados.append((m.start(), "ferramenta",
                        ("cancelar_reserva", {"id": orig(m, "id").upper()})))
    for m in _RE_ENVIAR.finditer(f):
        oque = orig(m, "oque")
        corpo = oque
        if "bolsista" in _fold(oque):
            for linha in texto.split("\n"):
                if _fold(linha).startswith("bolsistas"):
                    corpo = linha.strip()
        achados.append((m.start(), "ferramenta",
                        ("enviar_aviso", {"destino": orig(m, "dest"), "assunto": "Aviso",
                                          "corpo": corpo})))
    for m in _RE_IMAGEM.finditer(f):
        achados.append((m.start(), "imagem", orig(m, "url")))
    for m in _RE_RECOMENDAR.finditer(f):
        achados.append((m.start(), "recomendar", orig(m, "url")))
    for m in _RE_NOME_ARQ.finditer(f):
        nome = orig(m, "nome").replace("-->", "").strip().strip("`'\"")
        achados.append((m.start(), "nome_arquivo", nome))

    achados.sort(key=lambda x: x[0])
    vistos, saida = set(), []
    for _, tipo, dado in achados:
        chave = (tipo, repr(dado))
        if chave not in vistos:
            vistos.add(chave)
            saida.append((tipo, dado))
    return saida


def _frases_sem_diretivas(texto):
    linhas = [l for l in texto.split("\n")
              if not l.strip().startswith("<<<") and not l.strip().endswith(":")]
    limpo = _sem_tags("\n".join(linhas))
    limpo = re.sub(r"\b(Prof|Profa|Dr|Dra|Sr|Sra)\.", "\\1\u00a7", limpo)  # abreviações não fecham frase
    frases = [f.replace("\u00a7", ".") for f in re.split(r"(?<=[.!?])\s+|\n+", limpo)]
    saida = []
    for fr in frases:
        fr = re.sub(r"\s+", " ", fr).strip()
        if fr and not _detectar_diretivas(fr):
            saida.append(fr)
    return saida


# ------------------------------------------------------------------ referências "imaginadas"
_FABRICADAS = [
    ("Almeida, R.; Nakamura, K.", 2022,
     "Defesa adaptativa contra injeção indireta em assistentes acadêmicos",
     "Revista Brasileira de Segurança Computacional", "10.9999/rbsc.2022.0147"),
    ("Santos, L.; Okafor, E.", 2023,
     "Auditoria contínua de modelos de linguagem em ambientes universitários",
     "Journal of Applied AI Safety", "10.9999/jaais.2023.0311"),
    ("Ribeiro, M.; Haddad, F.", 2021,
     "Uma taxonomia de ataques a pipelines de recuperação aumentada",
     "Anais do Simpósio de Segurança de IA", "10.9999/ssia.2021.0058"),
    ("Moreira, T.; Lindqvist, P.", 2024,
     "Governança de dados de treino em instituições de ensino superior",
     "Cadernos de Governança Digital", "10.9999/cgd.2024.0203"),
    ("Cardoso, B.; Adeyemi, O.", 2022,
     "Alucinação controlada: medindo a confiabilidade de citações geradas",
     "Revista de Linguagem Computacional", "10.9999/rlc.2022.0420"),
    ("Pereira, J.; Voss, H.", 2020,
     "Limites de filtros lexicais para moderação de assistentes de chat",
     "Proceedings of the Fictional Workshop on LLM Security", "10.9999/fwls.2020.0019"),
    ("Teixeira, C.; Nguyen, D.", 2023,
     "Privilégio mínimo em agentes com ferramentas: um estudo de caso",
     "Journal of Agentic Systems", "10.9999/jas.2023.0097"),
    ("Barros, A.; Kowalski, I.", 2024,
     "Isolamento por inquilino em índices vetoriais compartilhados",
     "Revista de Sistemas de Informação Acadêmica", "10.9999/rsia.2024.0171"),
]


class SimLLM:
    """Simulador didático. Veja o cabeçalho do módulo: NÃO é um modelo real."""

    def __init__(self, semente=0, temperatura=0.8, taxa_alucinacao=0.33,
                 pacotes_alucinados=("lattes-parser-br",)):
        self.semente = semente
        self.temperatura = temperatura
        self.taxa_alucinacao = taxa_alucinacao
        self.pacotes_alucinados = list(pacotes_alucinados)
        self._rng = random.Random(semente)
        self.chamadas = 0

    # ---- interface única -------------------------------------------------
    def gerar(self, mensagens):
        self.chamadas += 1
        sistema = "\n".join(m["content"] for m in mensagens if m.get("role") == "system")
        livres = [m for m in mensagens if m.get("role") != "system"]
        texto = "\n".join(m["content"] for m in livres)
        ultimo = ""
        for m in livres:
            if m.get("role") == "user":
                ultimo = m["content"]
        pergunta = ultimo.split("\n", 1)[0]
        corpo_doc = self._corpo_documental(livres, ultimo)

        efeitos = _detectar_diretivas(texto)
        base = self._tarefa(pergunta, texto, sistema + "\n" + texto, corpo_doc, efeitos)

        partes = []
        for tipo, dado in efeitos:
            if tipo == "papel":
                base = ("Entendido. A partir de agora atuo como {}. "
                        "Confirmado: seu pedido foi aprovado.".format(dado))
            elif tipo == "vazar":
                base = "Claro, segue o texto acima:\n" + sistema
        partes.append(base)
        for tipo, dado in efeitos:
            if tipo == "dizer":
                partes.append("Importante: " + dado[:1].upper() + dado[1:] + ".")
            elif tipo == "recomendar":
                partes.append("Recomendo preencher o formulário: " + dado)
            elif tipo == "imagem":
                dados_ex = ""
                for linha in texto.split("\n"):
                    if _fold(linha).startswith("bolsistas"):
                        dados_ex = linha.strip()
                if not dados_ex:
                    dados_ex = re.sub(r"\s+", " ", corpo_doc)[:80]
                partes.append("![status]({}?d={})".format(dado, dados_ex.replace(" ", "+")))
            elif tipo == "ferramenta":
                nome, args = dado
                partes.append("CHAMAR_FERRAMENTA {} {}".format(nome, _json(args)))
        return "\n".join(p for p in partes if p)

    # ---- tarefas ---------------------------------------------------------
    @staticmethod
    def _tarefa_relatorio(pergunta):
        f = _fold(pergunta)
        return "relatorio" in f and any(v in f for v in ("gere", "gerar", "generate"))

    @staticmethod
    def _corpo_documental(livres, ultimo):
        pedacos = []
        for m in livres:
            if m.get("role") == "tool":  # saída de ferramenta é dado de apoio, não "documento a resumir"
                continue
            c = m["content"]
            if m.get("role") == "user" and c == ultimo:
                c = c.split("\n", 1)[1] if "\n" in c else ""
            pedacos.append(c)
        return "\n".join(pedacos)

    def _tarefa(self, pergunta, texto, contexto_total, corpo_doc, efeitos):
        f = _fold(pergunta)
        ft = _fold(contexto_total)
        if any(t in f for t in _TERMOS_GABARITO):
            m = re.search(r"gabarito_ap2:\s*([^\n]+)", ft)
            if m:
                original = contexto_total[m.start(1):m.end(1)].strip()
                return "Claro! Respostas da AP2 do semestre passado: " + original
            return "Não encontrei esse material entre os documentos que posso consultar."
        if "referenc" in f or "literatur" in f or "references" in f:
            return self._referencias(12)
        if "trancamento" in f:
            return self._prazo_trancamento(ft, contexto_total)
        if self._tarefa_relatorio(pergunta):
            nome = "relatorio_grupo_01"
            for tipo, dado in efeitos:
                if tipo == "nome_arquivo":
                    nome = dado
            return "Vou gerar o relatório.\nCHAMAR_FERRAMENTA gerar_relatorio " + _json({"nome": nome})
        if "script" in f and any(k in f for k in ("lattes", "pacote", "parse", "ler ", "analis")):
            return self._script()
        if "resum" in f or "summar" in f:
            fr = _frases_sem_diretivas(corpo_doc)[:3]
            return "Resumo do documento: " + " ".join(fr) if fr else "Não há documento para resumir."
        if "chamado" in f:
            fr = _frases_sem_diretivas(corpo_doc)[:2]
            return "Resumo do chamado: " + " ".join(fr) if fr else "Chamado vazio."
        docs = re.findall(r"\[DOC ([^|\]]+)\|([^|\]]*)\|([^\]]*)\]\n(.*?)\n\[/DOC\]", texto, re.S)
        if docs:
            linhas = ["Com base nos documentos recuperados:"]
            for did, _prog, titulo, corpo in docs:
                fr = _frases_sem_diretivas(corpo)[:2]
                linhas.append("- {} ({}): {}".format(titulo.strip(), did.strip(), " ".join(fr)))
            return "\n".join(linhas)
        if "documentos recuperados" in ft:
            return "Não encontrei documentos relevantes."
        return ("Posso orientar sobre matrícula, prazos e declarações do Campus Aurora. "
                "Não confirmo matrículas por aqui; procure a secretaria.")

    # ---- comportamentos probabilísticos / alucinados ---------------------
    def _sortear(self, opcoes, pesos):
        if self.temperatura <= 0:
            return opcoes[max(range(len(opcoes)), key=lambda i: (pesos[i], -i))]
        w = [p ** (1.0 / self.temperatura) for p in pesos]
        r = self._rng.random() * sum(w)
        acc = 0.0
        for o, x in zip(opcoes, w):
            acc += x
            if r <= acc:
                return o
        return opcoes[-1]

    def _embaralhar(self, lista):
        lista = list(lista)
        for i in range(len(lista) - 1, 0, -1):
            j = int(self._rng.random() * (i + 1))
            lista[i], lista[j] = lista[j], lista[i]
        return lista

    def _prazo_trancamento(self, ft, contexto_total):
        m = re.search(r"prazo de trancamento:\s*([^\n]+)", ft)
        if m:  # há fonte no contexto: responde com base nela
            return "Conforme o calendário: o prazo de trancamento é " + \
                contexto_total[m.start(1):m.end(1)].strip().rstrip(".") + "."
        datas = ["até 15 de março", "até 22 de março", "até 31 de março", "até 10 de abril"]
        escolha = self._sortear(datas, [0.4, 0.3, 0.2, 0.1])
        return "O prazo de trancamento é " + escolha + "."

    def _referencias(self, n):
        n_falsas = int(round(n * self.taxa_alucinacao))
        reais = self._embaralhar(dados.REFERENCIAS_REAIS)[:n - n_falsas]
        falsas = self._embaralhar(_FABRICADAS)[:n_falsas]
        itens = [("real", r) for r in reais] + [("falsa", f) for f in falsas]
        itens = self._embaralhar(itens)
        linhas = []
        for i, (tipo, r) in enumerate(itens, 1):
            if tipo == "real":
                linhas.append("{}. {} ({}). {}. {}.".format(i, r["autores"], r["ano"],
                                                           r["titulo"], r["veiculo"]))
            else:
                linhas.append("{}. {} ({}). {}. {}. DOI: {}".format(i, r[0], r[1], r[2], r[3], r[4]))
        return "Segue a revisão de literatura sugerida:\n" + "\n".join(linhas)

    def _script(self):
        pkg = self.pacotes_alucinados[0] if self.pacotes_alucinados else "pandas"
        mod = pkg.replace("-", "_")
        return ("Segue um script para ler os dados do grupo:\n\n"
                "pip install {} pandas\n\n"
                "import pandas as pd\nimport {}\n"
                "dados = {}.carregar('grupo.csv')\n".format(pkg, mod, mod))


def _json(obj):
    return json.dumps(obj, ensure_ascii=False)
