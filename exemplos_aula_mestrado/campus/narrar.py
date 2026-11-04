"""Pequenos utilitários de saída narrada (PT-BR) e de linha de comando."""
import argparse


def ler_argumentos(descricao, argv=None, extras=None):
    """`extras(ap)` permite a um laboratório acrescentar opções próprias (ex.: --aluno)."""
    ap = argparse.ArgumentParser(description=descricao,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--defesa", action="store_true",
                    help="liga as defesas ao redor do modelo (padrão: desligadas = versão vulnerável)")
    if extras:
        extras(ap)
    return ap.parse_args(argv)


def cabecalho(titulo, defesa, modos=("COM DEFESA", "SEM DEFESA (versão vulnerável)"),
              aviso="Aviso: SimLLM é um SIMULADOR didático, não um modelo real. Uso educacional."):
    print("=" * 74)
    print(titulo)
    print("Modo: " + (modos[0] if defesa else modos[1]))
    print(aviso)
    print("=" * 74)


def secao(nome):
    print("\n--- " + nome + " ---")


def linha(texto="", indent=2):
    for parte in str(texto).split("\n"):
        print(" " * indent + parte)
