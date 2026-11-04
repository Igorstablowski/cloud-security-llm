import os
import subprocess
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABS = ["aula5/lab1_gerar_e_sortear.py", "aula5/lab2_canal_unico.py", "aula5/lab3_acervo_rag.py",
        "aula5/lab4_agente_agenda.py", "aula6/lab5_dados_na_fronteira.py",
        "aula6/lab6_queijo_suico.py", "aula6/lab7_avaliacao.py"]


@pytest.mark.parametrize("lab", LABS)
@pytest.mark.parametrize("flag", [[], ["--defesa"]])
def test_cli_roda_e_imprime_secoes_narradas(lab, flag):
    out = subprocess.run([sys.executable, os.path.join(RAIZ, lab)] + flag, capture_output=True,
                         text=True, cwd=RAIZ, timeout=60)
    assert out.returncode == 0, out.stderr
    for secao in ("ATAQUE", "O QUE ACONTECEU", "O QUE OBSERVAR"):
        assert secao in out.stdout
