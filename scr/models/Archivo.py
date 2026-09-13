import json
from Nodo import Nodo
from AVL import AVL
from typing import Optional
from Event import Event



def guardar_sismos (sismos):
    with open("sismos.json", "w") as archivo:
        json.dumb(sismos, archivo, ident=4)

def cargar_sismos():
    with open("sismos.json", "r") as archivo:
        return json.load(archivo)


evento1= Event (
    100,
    5.0,
    20.0,
    (300.0 , 400.0),
    "2026-09-13",
    1,
    {"sta01"},
    "pending"
)

evento2= Event (
    200,
    5.0,
    20.0,
    (300.0 , 400.0),
    "2026-09-13",
    1,
    {"sta01"},
    "pending"
)
evento3= Event (
    300,
    5.0,
    20.0,
    (300.0 , 400.0),
    "2026-09-13",
    1,
    {"sta01"},
    "pending"
)

evento4= Event (
    400,
    5.0,
    20.0,
    (300.0 , 400.0),
    "2026-09-13",
    1,
    {"sta01"},
    "pending"
)
evento5= Event (
    500,
    5.0,
    20.0,
    (300.0 , 400.0),
    "2026-09-13",
    1,
    {"sta01"},
    "pending"
)

evento6= Event (
    600,
    5.0,
    20.0,
    (300.0 , 400.0),
    "2026-09-13",
    1,
    {"sta01"},
    "pending"
)


arbol=AVL()
arbol.insertar(evento1)
arbol.insertar(evento2)
arbol.insertar(evento3)
arbol.insertar(evento4)
arbol.insertar(evento5)
arbol.insertar(evento6)

"""
lista=arbol.anchura()
for evento in lista:
    print(evento)

print(" ")

arbol.balancear()

lista=arbol.anchura()
for evento in lista:
    print(evento)
print (" ")
"""

arbol.eliminar(evento3)

lista=arbol.anchura()
for evento in lista:
    print(evento)

print(" ")

arbol.balancear()

lista=arbol.anchura()
for evento in lista:
    print(evento)
print (" ")

