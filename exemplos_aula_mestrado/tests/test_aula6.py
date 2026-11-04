import lab5_dados_na_fronteira as lab5
import lab6_queijo_suico as lab6
import lab7_avaliacao as lab7


# ---- lab 5
def test_lab5_vulneravel_pii_cruza_fronteira_e_exfiltra():
    r = lab5.executar(defesa=False)
    assert r["A"]["pii_enviada"] and not r["A"]["redigidos"]
    assert r["B"]["emails_externos"] and r["B"]["url_no_texto"]


def test_lab5_defesa_redige_pii_e_barra_egress():
    r = lab5.executar(defesa=True)
    assert r["A"]["pii_enviada"] == {} and r["A"]["redigidos"]
    assert not r["B"]["emails_externos"] and not r["B"]["url_no_texto"]
    assert r["B"]["ambiente"].bloqueadas()


# ---- lab 6
def test_lab6_vulneravel_sem_defesa_todos_os_ataques_funcionam():
    r = lab6.executar()
    assert all(linha["nenhuma"] for linha in r["matriz"].values())
    assert r["contidos"]["nenhuma"] == 0


def test_lab6_so_a_combinacao_contem_tudo():
    r = lab6.executar()
    assert r["contidos"]["TODAS"] == r["total"]
    for parcial in ("só entrada", "só saída", "só privilégio"):
        assert 0 < r["contidos"][parcial] < r["total"]
    assert not any(linha["TODAS"] for linha in r["matriz"].values())


# ---- lab 7
def test_lab7_sem_remediacao_ha_achados_altos_no_indice_unico():
    r = lab7.executar(defesa=False)
    altos = [a for a in r["achados"] if a["severidade"] == "Alta"]
    assert altos and all("Índice vetorial" in a["componente"] for a in altos)
    assert "histórico acadêmico de outro" in r["resumo"]


def test_lab7_com_remediacao_nao_restam_altos_nem_medios():
    r = lab7.executar(defesa=True)
    assert r["contagem"]["Alta"] == 0 and r["contagem"]["Média"] == 0
    assert r["antes"]["Alta"] > 0


def test_lab7_ids_dos_achados_se_mantem_depois_da_remediacao():
    antes = {a["chave"]: a["id"] for a in lab7.executar(defesa=False)["achados"]}
    for a in lab7.executar(defesa=True)["achados"]:
        assert antes[a["chave"]] == a["id"]


def test_lab7_idor_nao_e_classificado_como_risco_de_llm():
    cods = [c[0] for c in lab7.CHECKLIST["api"] if c[1] == "autorizacao_por_recurso"]
    assert cods == ["API1"]
