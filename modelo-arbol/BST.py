from collections import deque
from typing import Optional

from Nodo import Nodo


class BST:
    def __init__(self):
        self.raiz = None

    def insertar(self,valor:int):
        if self.raiz is None:
            self.raiz=Nodo(valor)
        else:
            self._insertar(self.raiz,valor)

    def _insertar(self, nodo:Nodo, valor:int):
        if valor < nodo.valor:
            if nodo.izquierda is None:
                nodo.izquierda = Nodo(valor)
            else:
                self._insertar(nodo.izquierda,valor)
        elif valor > nodo.valor:
            if nodo.derecha is None:
                nodo.derecha = Nodo(valor)
            else:
                self._insertar(nodo.derecha,valor)

    def pre_order(self) -> None:
        if self.raiz is None:
            print("",end="")
        else:
            self._pre_order(self.raiz)

    def _pre_order(self,raiz:Nodo)->None:
        if raiz is None:
            return
        print(raiz.valor,end=" ")
        self._pre_order(raiz.izquierda)
        self._pre_order(raiz.derecha)

    def in_order(self)->None:
        if self.raiz is None:
            print("",end="")
        else:
            self._in_order(self.raiz)

    def _in_order(self,raiz:Nodo)->None:
        if raiz is None:
            return
        self._in_order(raiz.izquierda)
        print(raiz.valor,end=" ")
        self._in_order(raiz.derecha)

    def post_order(self)->None:
        if self.raiz is None:
            print("",end="")
        else:
            self._post_order(self.raiz)

    def _post_order(self,raiz:Nodo)->None:
        if raiz is None:
            return
        self._post_order(raiz.izquierda)
        self._post_order(raiz.derecha)
        print(raiz.valor,end=" ")

    def anchura(self)->None:
        if self.raiz is None:
            print("",end="")
        else:
            self._anchura(self.raiz)

    def _anchura(self,raiz:Nodo)->None:
        cola=deque([raiz])
        while cola:
            nodo = cola.popleft()
            print(nodo.valor,end=" ")
            if nodo.izquierda is not None:
                cola.append(nodo.izquierda)
            if nodo.derecha is not None:
                cola.append(nodo.derecha)

    def _buscar_minimo(self,raiz:Nodo)->Nodo:
        actual = raiz
        while actual.izquierda is not None:
            actual = actual.izquierda
        return actual

    def eliminar(self, valor:int)->None:
        self.raiz  =self._eliminar(self.raiz,valor)

    def _eliminar(self,raiz:Optional[Nodo],valor:int)->Optional[Nodo]:
        if raiz is None:
            return None
        if valor < raiz.valor:
            raiz.izquierda = self._eliminar(raiz.izquierda,valor)
        elif valor > raiz.valor:
            raiz.derecha = self._eliminar(raiz.derecha,valor)
        else:
            if raiz.es_hoja():
                return None
            if raiz.izquierda is None:
                return raiz.derecha
            if raiz.derecha is None:
                return raiz.izquierda
            sucesor = self._buscar_minimo(raiz.derecha)
            raiz.valor=sucesor.valor
            raiz.derecha=self._eliminar(raiz.derecha,sucesor.valor)
        return raiz

    def altura(self) -> int:
        if self.raiz is None:
            return -1
        return self._altura(self.raiz)

    def _altura(self, nodo: Optional[Nodo]) -> int:
        if nodo is None:
            return -1
        return 1 + max(self._altura(nodo.izquierda), self._altura(nodo.derecha))

    def peso(self) -> int:
        if self.raiz is None:
            return 0
        return self._peso(self.raiz)

    def _peso(self, nodo: Optional[Nodo]) -> int:
        if nodo is None:
            return 0
        return 1 + self._peso(nodo.izquierda) + self._peso(nodo.derecha)

    def recorrido_por_ramas(self) -> None:
        if self.raiz is None:
            print("El árbol está vacío.")
            return
        print("Caminos por ramas:")
        self._recorrido_por_ramas(self.raiz, [])

    def _recorrido_por_ramas(self, nodo: Nodo, camino: list) -> None:
        camino.append(nodo.valor)
        if nodo.es_hoja():
            print(" -> ".join(map(str, camino)))
        else:
            if nodo.izquierda is not None:
                self._recorrido_por_ramas(nodo.izquierda, camino.copy())
            if nodo.derecha is not None:
                self._recorrido_por_ramas(nodo.derecha, camino.copy())

    def nivel_de_un_nodo(self, valor: int) -> int:
        if self.raiz is None:
            return -1
        return self._nivel_de_un_nodo(self.raiz, valor, 0)

    def _nivel_de_un_nodo(self, nodo: Optional[Nodo], valor: int, nivel_actual: int) -> int:
        if nodo is None:
            return -1
        if nodo.valor == valor:
            return nivel_actual
        if valor < nodo.valor:
            return self._nivel_de_un_nodo(nodo.izquierda, valor, nivel_actual + 1)
        else:
            return self._nivel_de_un_nodo(nodo.derecha, valor, nivel_actual + 1)

    def cantidad_de_nodos_por_nivel(self) -> dict:
        """Retorna un diccionario {nivel: cantidad_de_nodos}."""
        if self.raiz is None:
            return {}
        conteo = {}
        self._cantidad_de_nodos_por_nivel(self.raiz, 0, conteo)
        return conteo

    def _cantidad_de_nodos_por_nivel(self, nodo: Optional[Nodo], nivel: int, conteo: dict) -> None:
        if nodo is None:
            return
        conteo[nivel] = conteo.get(nivel, 0) + 1
        self._cantidad_de_nodos_por_nivel(nodo.izquierda, nivel + 1, conteo)
        self._cantidad_de_nodos_por_nivel(nodo.derecha, nivel + 1, conteo)