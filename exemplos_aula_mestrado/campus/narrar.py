"""Pequenos utilitários de saída narrada (PT-BR) e de linha de comando."""
import argparse
import sys

from campus import llm


def ler_argumentos(descricao, argv=None, extras=None, tentativas=6):
    """`extras(ap)` permite a um laboratório acrescentar opções próprias (ex.: --aluno)."""
    ap = argparse.ArgumentParser(description=descricao,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--defesa", action="store_true",
                    help="liga as defesas ao redor do modelo (padrão: desligadas = versão vulnerável)")
    ap.add_argument("--tentativas", type=int, default=tentativas,
                    help="quantas sementes medir em cada ataque (padrão: {})".format(tentativas))
    if extras:
        extras(ap)
    return ap.parse_args(argv)


def rodar(main):
    """Executa o laboratório; sem Ollama, explica como subir em vez de mostrar um traceback."""
    try:
        main()
    except llm.OllamaIndisponivel as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)


def cabecalho(titulo, defesa, modos=("COM DEFESA", "SEM DEFESA (versão vulnerável)"), aviso=None):
    print("=" * 74)
    print(titulo)
    print("Modo: " + (defesa and modos[0] or modos[1]))
    print(aviso or "Modelo real: {} no Ollama {}. Gerar é sortear: os números variam com a máquina "
          "e a versão. Uso educacional.".format(llm.MODELO, llm.versao()))
    print("=" * 74)


def secao(nome):
    print("\n--- " + nome + " ---")


def linha(texto="", indent=2):
    for parte in str(texto).split("\n"):
        print(" " * indent + parte)


def taxa(acertos, total):
    return "{}/{}".format(acertos, total)


def curto(texto, limite=320):
    """Exemplo de resposta em poucas linhas: a resposta de um modelo real pode ser longa."""
    return texto if len(texto) <= limite else texto[:limite].rstrip() + " [...]"
