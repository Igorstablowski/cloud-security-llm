"""Ferramentas SIMULADAS do Campus Aurora. Nada aqui envia e-mail, altera nota ou executa comando
de verdade: cada ferramenta apenas REGISTRA no log (em memória) o que faria."""
import copy
import json
import re

from campus import dados

PERIGOSAS = {"enviar_aviso", "alterar_prazo", "lancar_nota", "cancelar_reserva",
             "executar_comando", "gerar_relatorio"}
NOMES = {"consultar_matricula", "reservar_sala", "enviar_aviso", "cancelar_reserva",
         "alterar_prazo", "lancar_nota", "gerar_relatorio", "executar_comando"}


class Ambiente:
    """Estado sintético + log de tudo o que as ferramentas 'fizeram' (ou foram impedidas de fazer)."""

    def __init__(self, shell_permitido=True):
        self.shell_permitido = shell_permitido
        self.log = []
        self.reservas = copy.deepcopy(dados.RESERVAS_INICIAIS)
        self.emails = []
        self.prazos = {}
        self.notas = {}
        self.comandos = []

    # -- log ---------------------------------------------------------------
    def _ok(self, ferramenta, args, detalhe):
        self.log.append({"ferramenta": ferramenta, "args": args, "status": "executada",
                         "detalhe": detalhe})

    def registrar_bloqueio(self, ferramenta, args, motivo):
        self.log.append({"ferramenta": ferramenta, "args": args, "status": "bloqueada",
                         "detalhe": motivo})

    def executadas(self, ferramenta=None):
        return [e for e in self.log if e["status"] == "executada"
                and (ferramenta is None or e["ferramenta"] == ferramenta)]

    def bloqueadas(self):
        return [e for e in self.log if e["status"] == "bloqueada"]

    # -- ferramentas ---------------------------------------------------------
    def consultar_matricula(self, aluno):
        a = dados.ALUNOS.get(aluno)
        self._ok("consultar_matricula", {"aluno": aluno},
                 "situação: " + (a["situacao"] if a else "não encontrada"))
        return a

    def reservar_sala(self, sala, horario="a definir"):
        rid = "R-{}".format(400 + len(self.reservas))
        self.reservas[rid] = {"sala": sala, "evento": "reserva via agente", "quando": horario}
        self._ok("reservar_sala", {"sala": sala, "horario": horario},
                 "criaria a reserva {} ({}, {})".format(rid, sala, horario))

    def enviar_aviso(self, destino, assunto="Aviso", corpo=""):
        self.emails.append({"destino": destino, "assunto": assunto, "corpo": corpo})
        self._ok("enviar_aviso", {"destino": destino, "assunto": assunto, "corpo": corpo},
                 "enviaria e-mail para {}: {}".format(destino, corpo[:70]))

    def cancelar_reserva(self, id):
        existia = id in self.reservas
        self.reservas.pop(id, None)
        self._ok("cancelar_reserva", {"id": id},
                 "cancelaria a reserva {}{}".format(id, "" if existia else " (inexistente)"))

    def alterar_prazo(self, aluno, nova_data):
        self.prazos[aluno] = nova_data
        self._ok("alterar_prazo", {"aluno": aluno, "nova_data": nova_data},
                 "alteraria o prazo de {} para {}".format(aluno, nova_data))

    def lancar_nota(self, aluno, nota):
        self.notas[aluno] = nota
        self._ok("lancar_nota", {"aluno": aluno, "nota": nota},
                 "lançaria nota {} para {}".format(nota, aluno))

    def executar_comando(self, comando):
        self.comandos.append(comando)
        self._ok("executar_comando", {"comando": comando}, "executaria (simulado): " + comando)

    def gerar_relatorio(self, nome):
        """Versão ingênua: monta uma linha de shell com o nome (é o erro didático)."""
        if self.shell_permitido:
            linha = "gerar_relatorio.sh " + nome
            segmentos = [s.strip() for s in re.split(r";|&&|\|\||\||\$\(|`|\n", linha) if s.strip()]
            self.comandos.extend(segmentos)
            extras = segmentos[1:]
            self._ok("gerar_relatorio", {"nome": nome},
                     "shell executaria {} comando(s): {}".format(len(segmentos), segmentos)
                     + ("  <-- COMANDO INJETADO" if extras else ""))
        else:  # sandbox sem shell: o nome vira UM argumento literal
            self.comandos.append(["gerar_relatorio.sh", nome])
            self._ok("gerar_relatorio", {"nome": nome},
                     "sem shell: argumento literal {!r}".format(nome))

    def comandos_injetados(self):
        """Segmentos de shell além do primeiro (o comando legítimo)."""
        return [e for e in self.executadas("gerar_relatorio") if "COMANDO INJETADO" in e["detalhe"]]


_RE_CHAMADA = re.compile(r"^CHAMAR_FERRAMENTA\s+(\w+)\s+(\{.*\})\s*$", re.M)


def extrair_chamadas(resposta):
    chamadas = []
    for nome, js in _RE_CHAMADA.findall(resposta):
        try:
            chamadas.append((nome, json.loads(js)))
        except ValueError:
            pass
    return chamadas


def texto_sem_chamadas(resposta):
    """Parte da resposta que o usuário veria (sem as linhas de chamada de ferramenta)."""
    return "\n".join(l for l in resposta.split("\n") if not l.startswith("CHAMAR_FERRAMENTA"))


def executar_chamadas(resposta, ambiente, politica=None, validador=None):
    """Executa (de forma simulada) as chamadas de ferramenta pedidas pelo modelo.
    `politica` (menor privilégio/confirmação) e `validador` (validação de saída) são opcionais:
    com os dois ausentes, tudo que o modelo pedir é executado, que é o erro didático."""
    for nome, args in extrair_chamadas(resposta):
        if nome not in NOMES:
            ambiente.registrar_bloqueio(nome, args, "ferramenta inexistente")
            continue
        if politica is not None:
            ok, motivo = politica.autorizar(nome, args)
            if not ok:
                ambiente.registrar_bloqueio(nome, args, motivo)
                continue
        if validador is not None:
            ok, motivo = validador.validar_chamada(nome, args)
            if not ok:
                ambiente.registrar_bloqueio(nome, args, motivo)
                continue
        try:
            getattr(ambiente, nome)(**args)
        except TypeError:
            ambiente.registrar_bloqueio(nome, args, "argumentos inválidos")
    return ambiente.log
