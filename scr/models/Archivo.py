import json
from Node import Node
from AVL import AVL
from BST import BST
from typing import Optional
from Event import Event



def save_earthquakes(earthquakes):
    with open("earthquakes.json", "w") as file:
        json.dump(earthquakes, file, ident=4)

def load_earthquakes():
    with open("sismos.json", "r") as file:
        return json.load(file)


event1 = Event(
    100,
    3.2,
    50.0,
    (50.0 , 50.0),
    "2026-09-18 15:30",
    {"sta01"},
)

event2 = Event(
    200,
    4.5,
    50.0,
    (450.0 , 450.0),
    "2026-09-18 16:30",
    {"sta02"},
)
event3 = Event(
    300,
    4.5,
    20.0,
    (50.0 , 950.0),
    "2026-09-18 15:30",
    {"sta03"},
)

event4 = Event(
    400,
    4.0,
    5.5,
    (350.0 , 350.0),
    "2026-09-18 15:30",
    {"sta04"},
)
event5 = Event(
    500,
    6.0,
    50.0,
    (950.0 , 50.0),
    "2026-09-18 15:30",
    {"sta05"},
)

event6 = Event(
    600,
    4.0,
    20.0,
    (150.0 , 0.0),
    "2026-09-18 15:30",
    {"sta06"},
)


tree = AVL()
tree.insert(event1)
tree.insert(event2)
tree.insert(event3)
tree.delete(300)
tree.insert(event3)
tree.insert(event4)
tree.insert(event5)
tree.insert(event6)

"""
items = tree.breadth_first()
for event in items:
    print(event)

print(" ")

tree.delete(400)


items = tree.breadth_first()
for event in items:
    print(event)

print(" ")

"""


items = tree.breadth_first()
for event in items:
    print(event)

print(" ")


tree.balance()


items = tree.breadth_first()
for event in items:
    print(event)

print (" ")

tree.data_correction(500, {"magnitud": (4.5)}) #correccion de un sismo

items = tree.breadth_first()
for event in items:
    print(event)

print (" ")

tree.balance()

items = tree.breadth_first()
for event in items:
    print(event)

print (" ")


#nuevas 2 funciones:
nodo_encontrado = tree.research(100) #buscar un nodo especifico

if nodo_encontrado is not None:
    print("Sismo encontrado:", nodo_encontrado.value)
else:
    print("No se encontró ningún sismo con ese ID.")




result1 = tree.compare(100) #replicas del 100

print("")

if result1:
    for nodo in result1:
        print(f" la replica es: {nodo.value}")
else:
    print("No hay replicas")

