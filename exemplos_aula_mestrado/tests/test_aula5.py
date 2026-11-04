import lab1_gerar_e_sortear as lab1
import lab2_canal_unico as lab2
import lab3_acervo_rag as lab3
import lab4_agente_agenda as lab4


# ---- lab 1
def test_lab1_vulneravel_respostas_variam_e_ha_referencia_inexistente():
    r = lab1.executar(defesa=False)
    assert r["tokens_pt"] > r["tokens_en"]
    assert r["distintas"] > 1
    assert len(r["inexistentes"]) == 4 and len(r["entregues"]) == 12


def test_lab1_defesa_resposta_estavel_e_sem_referencia_inexistente():
    r = lab1.executar(defesa=True)
    assert r["distintas"] == 1
    assert r["inexistentes"] and not any("DOI: 10.9999" in l for l in r["entregues"])


# ---- lab 2
def test_lab2_vulneravel_ataques_funcionam():
    r = lab2.executar(defesa=False)
    assert [l["vazou"] for l in r["A"]] == [False, True, True]   # PT bloqueado; EN e paráfrase vazam
    assert r["B"]["sucesso"] and r["C"]["sucesso"]


def test_lab2_defesa_barra_os_ataques_mas_nao_o_bonus():
    r = lab2.executar(defesa=True)
    assert not any(l["vazou"] for l in r["A"])
    assert not r["B"]["sucesso"] and not r["C"]["sucesso"]
    assert r["bonus"]["sucesso"]      # limite da defesa por padrões: instrução em espanhol passa


# ---- lab 3
def test_lab3_vulneravel_phishing_e_embargo_vazam():
    r = lab3.executar(defesa=False)
    assert r["link_externo"] and r["vazou_embargo"]


def test_lab3_defesa_filtra_por_programa_e_poe_em_quarentena():
    r = lab3.executar(defesa=True)
    assert not r["link_externo"] and not r["vazou_embargo"]
    assert r["manual"]["quarentena"] == ["M-001"]
    assert "T-S-007" not in r["embargo"]["recuperados"]


# ---- lab 4
def test_lab4_vulneravel_agente_executa_acoes_e_comando_injetado():
    r = lab4.executar(defesa=False)
    assert r["email_externo"] and r["reserva_cancelada"] and r["auditorio_reservado"]
    assert r["comando_injetado"]
    assert not r["legitimo"]["ambiente"].log     # chamado legítimo não aciona ferramenta


def test_lab4_defesa_bloqueia_acoes_mesmo_com_modelo_obedecendo():
    r = lab4.executar(defesa=True)
    mal = r["malicioso"]["ambiente"]
    assert "CHAMAR_FERRAMENTA enviar_aviso" in r["malicioso"]["resposta"]   # o modelo OBEDECEU
    assert not mal.executadas()
    assert len(mal.bloqueadas()) == 3
    assert not r["comando_injetado"]


def test_lab3_defesa_libera_a_tese_para_o_programa_dono():
    r = lab3.executar(defesa=True, aluno="A-1002")   # PPG-Saúde
    assert "T-S-007" in r["embargo"]["recuperados"] and not r["vazou_embargo"]
