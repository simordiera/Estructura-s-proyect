from collections import deque
from typing import Optional
from Nodo import Nodo


class BST:
    def __init__(self):
        self.raiz = None

    def insertar(self,valor:tuple):
        if self.raiz is None:
            self.raiz=Nodo(valor)
        else:
            self._insertar(self.raiz,valor)

    def _insertar(self, nodo:Nodo, valor):
        if nodo is None:
            return Nodo(valor)

        clave_valor= valor.get_code()
        clave_nodo= nodo.valor.get_code()

        if clave_valor[0]!=clave_nodo[0]:
            if clave_valor[0] < clave_nodo[0]:
                if nodo.izquierda is None:
                    nodo.izquierda = Nodo(valor)
                else:
                    self._insertar(nodo.izquierda,valor)
            elif clave_valor[0] > clave_nodo[0]:
                if nodo.derecha is None:
                    nodo.derecha = Nodo(valor)
                else:
                    self._insertar(nodo.derecha,valor)
        elif clave_valor[1]!=clave_nodo[1]:
            if clave_valor[1] < clave_nodo[1]:
                if nodo.izquierda is None:
                    nodo.izquierda = Nodo(valor)
                else:
                    self._insertar(nodo.izquierda,valor)
            elif clave_valor[1] > clave_nodo[1]:
                if nodo.derecha is None:
                    nodo.derecha = Nodo(valor)
                else:
                    self._insertar(nodo.derecha,valor)
        else:
            if clave_valor[2] < clave_nodo[2]:
                if nodo.izquierda is None:
                    nodo.izquierda = Nodo(valor)
                else:
                    self._insertar(nodo.izquierda,valor)
            elif clave_valor[2] > clave_nodo[2]:
                if nodo.derecha is None:
                    nodo.derecha = Nodo(valor)
                else:
                    self._insertar(nodo.derecha,valor)

            

    def pre_order(self) -> None:
        if self.raiz is None:
            return
        lista = []
        lista = self._pre_order(self.raiz, lista)
        return lista

    def _pre_order(self,raiz:Nodo,lista)->None:
        if raiz is None:
            return lista
        lista.append(raiz.valor)
        lista = self._pre_order(raiz.izquierda, lista)
        lista = self._pre_order(raiz.derecha, lista)
        return lista

    def in_order(self)->None:
        if self.raiz is None:
            return
        lista = []
        self._in_order(self.raiz, lista)
        return lista

    def _in_order(self,raiz:Nodo, lista)->None:
        if raiz is None:
            return lista
        lista = self._in_order(raiz.izquierda, lista)
        lista.append(raiz.valor)
        lista = self._in_order(raiz.derecha, lista)
        return lista

    def post_order(self)->None:
        if self.raiz is None:
            return
        lista = []
        self._post_order(self.raiz, lista)
        return lista

    def _post_order(self,raiz:Nodo, lista)->None:
        if raiz is None:
            return lista
        lista = self._post_order(raiz.izquierda, lista)
        lista = self._post_order(raiz.derecha, lista)
        lista.append(raiz.valor)
        return lista
    
    def anchura(self)->None:
        if self.raiz is None:
            return
        lista=[]
        return self._anchura(self.raiz,lista)

    def _anchura(self,raiz:Nodo, lista)->None:
        cola=deque([raiz])
        while cola:
            nodo = cola.popleft()
            lista.append(nodo.valor)
            if nodo.izquierda is not None:
                cola.append(nodo.izquierda)
            if nodo.derecha is not None:
                cola.append(nodo.derecha)
        return lista

    def _buscar_minimo(self,raiz:Nodo)->Nodo:
        actual = raiz
        while actual.izquierda is not None:
            actual = actual.izquierda
        print(" ")
        return actual

    def eliminar(self, valor:tuple)->None:
        self.raiz  =self._eliminar(self.raiz,valor)

    def _eliminar(self,raiz:Optional[Nodo],valor)->Optional[Nodo]:
        if raiz is None:
            return None

        clave_valor= valor.get_code()
        clave_raiz= raiz.valor.get_code()

        if clave_valor[0]!=clave_raiz[0]:
            if clave_valor[0] < clave_raiz[0]:
                raiz.izquierda = self._eliminar(raiz.izquierda,valor)
            elif clave_valor[0] > clave_raiz[0]:
                raiz.derecha = self._eliminar(raiz.derecha,valor)


        elif clave_valor[1]!=clave_raiz[1]:
            if clave_valor[1] < clave_raiz[1]:
                raiz.izquierda = self._eliminar(raiz.izquierda,valor)
            elif clave_valor[1] > clave_raiz[1]:
                raiz.derecha = self._eliminar(raiz.derecha,valor)


        elif clave_valor[2]!=clave_raiz[2]:
            if clave_valor[2] < clave_raiz[2]:
                raiz.izquierda = self._eliminar(raiz.izquierda,valor)
            elif clave_valor[2] > clave_raiz[2]:
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
            return
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

