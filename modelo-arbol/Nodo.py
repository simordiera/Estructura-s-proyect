from dataclasses import dataclass
from typing import Optional

@dataclass
class Nodo:
    valores = []
    izquierda : Optional['Nodo'] = None
    derecha : Optional['Nodo'] = None
    altura: int = 1

    def es_hoja(self)->bool:
        return self.izquierda is None and self.derecha is None