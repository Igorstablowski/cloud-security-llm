import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (RAIZ, os.path.join(RAIZ, "aula5"), os.path.join(RAIZ, "aula6")):
    if p not in sys.path:
        sys.path.insert(0, p)
