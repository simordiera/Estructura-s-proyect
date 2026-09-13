from collections import deque
from typing import Optional
from Nodo import Nodo


class AVL:

    def __init__(self):
        self.raiz = None


    def _obtener_altura(self, nodo: Optional[Nodo]) -> int:
        if nodo is None:
            return 0
        return nodo.altura

    def _actualizar_altura(self, nodo: Nodo) -> None:
        nodo.altura = 1 + max(
            self._obtener_altura(nodo.izquierda),
            self._obtener_altura(nodo.derecha)
        )


    def _factor_balance(self, nodo: Optional[Nodo]):
        if nodo is None:
            return 0

        return (
            self._obtener_altura(nodo.izquierda)
            - self._obtener_altura(nodo.derecha) )       

        

    def _rotacion_derecha(self, y: Nodo) -> Nodo:

        x = y.izquierda
        temporal = x.derecha

        x.derecha = y
        y.izquierda = temporal

        self._actualizar_altura(y)
        self._actualizar_altura(x)

        return x

    def _rotacion_izquierda(self, x: Nodo) -> Nodo:

        y = x.derecha
        temporal = y.izquierda

        y.izquierda = x
        x.derecha = temporal

        self._actualizar_altura(x)
        self._actualizar_altura(y)

        return y


    def insertar(self, valor) -> None:
        self.raiz = self._insertar(self.raiz, valor)

    def _insertar(self, nodo: Optional[Nodo], valor) -> Nodo:

        if nodo is None:
            return Nodo(valor)
        clave_valor= valor.get_code()
        clave_nodo= nodo.valor.get_code()
        
        if clave_valor[0]!=clave_nodo[0]:
            if clave_valor[0] < clave_nodo[0]:
                nodo.izquierda = self._insertar(nodo.izquierda, valor)

            elif clave_valor[0] > clave_nodo[0]:
                nodo.derecha = self._insertar(nodo.derecha, valor)

        elif clave_valor[1]!=clave_nodo[1]:
            if clave_valor[1] < clave_nodo[1]:
                nodo.izquierda = self._insertar(nodo.izquierda, valor)

            elif clave_valor[1] > clave_nodo[1]:
                nodo.derecha = self._insertar(nodo.derecha, valor)

        elif clave_valor[2]!=clave_nodo[2]:
            if clave_valor[2] < clave_nodo[2]:
                nodo.izquierda = self._insertar(nodo.izquierda, valor)

            elif clave_valor[2] > clave_nodo[2]:
                nodo.derecha = self._insertar(nodo.derecha, valor)  

        else:
            return nodo

        return nodo
        
    def balancear (self) -> None:
        self.raiz=self._balancear(self.raiz)

    def _balancear(self, nodo: Optional[Nodo]) -> Nodo:
        if nodo is None:
            return None

    
        nodo.izquierda = self._balancear(nodo.izquierda)

        nodo.derecha = self._balancear(nodo.derecha)

        
        self._actualizar_altura(nodo)
        balance = self._factor_balance(nodo)


        if balance > 1:

            if self._factor_balance(nodo.izquierda) >= 0:
                return self._rotacion_derecha(nodo)

            else:
                nodo.izquierda = self._rotacion_izquierda(
                    nodo.izquierda
                )

                return self._rotacion_derecha(nodo)

        if balance < -1:

            if self._factor_balance(nodo.derecha) <= 0:
                return self._rotacion_izquierda(nodo)
            else:
                nodo.derecha = self._rotacion_derecha(
                    nodo.derecha
                )

                return self._rotacion_izquierda(nodo)

        return nodo


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



    def post_order(self) -> None:

        if self.raiz is None:
            print("", end="")
        else:
            self._post_order(self.raiz)

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


    def _buscar_minimo(self, raiz: Nodo) -> Nodo:

        actual = raiz

        while actual.izquierda is not None:
            actual = actual.izquierda

        return actual


    def eliminar(self, valor) -> None:
        self.raiz = self._eliminar(self.raiz, valor)

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

    def _altura(
        self,
        nodo: Optional[Nodo]
    ) -> int:

        if nodo is None:
            return -1

        return 1 + max(
            self._altura(nodo.izquierda),
            self._altura(nodo.derecha)
        )


    def peso(self) -> int:

        if self.raiz is None:
            return 0

        return self._peso(self.raiz)

    def _peso(
        self,
        nodo: Optional[Nodo]
    ) -> int:

        if nodo is None:
            return 0

        return (
            1
            + self._peso(nodo.izquierda)
            + self._peso(nodo.derecha)
        )


    def nivel_de_un_nodo(
        self,
        valor: int
    ) -> int:

        if self.raiz is None:
            return -1

        return self._nivel_de_un_nodo(
            self.raiz,
            valor,
            0
        )

    def _nivel_de_un_nodo(
        self,
        nodo: Optional[Nodo],
        valor: int,
        nivel_actual: int
    ) -> int:

        if nodo is None:
            return -1

        if nodo.valor == valor:
            return nivel_actual

        if valor < nodo.valor:

            return self._nivel_de_un_nodo(
                nodo.izquierda,
                valor,
                nivel_actual + 1
            )

        else:

            return self._nivel_de_un_nodo(
                nodo.derecha,
                valor,
                nivel_actual + 1
            )


    def cantidad_de_nodos_por_nivel(self) -> dict:

        if self.raiz is None:
            return {}

        conteo = {}

        self._cantidad_de_nodos_por_nivel(
            self.raiz,
            0,
            conteo
        )

        return conteo

    def _cantidad_de_nodos_por_nivel(
        self,
        nodo: Optional[Nodo],
        nivel: int,
        conteo: dict
    ) -> None:

        if nodo is None:
            return

        conteo[nivel] = (
            conteo.get(nivel, 0) + 1
        )

        self._cantidad_de_nodos_por_nivel(
            nodo.izquierda,
            nivel + 1,
            conteo
        )

        self._cantidad_de_nodos_por_nivel(
            nodo.derecha,
            nivel + 1,
            conteo
        )