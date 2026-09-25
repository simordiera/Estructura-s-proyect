import json
from Node import Node
from AVL import AVL
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
    4.0,
    20.0,
    (300.0 , 400.0),
    "2026-09-18 15:30",
    1,
    {"sta01"},
    "pending"
)

event2 = Event(
    200,
    2.0,
    20.0,
    (340.0 , 400.0),
    "2026-09-18 16:30",
    1,
    {"sta02"},
    "pending"
)
event3 = Event(
    300,
    3.0,
    20.0,
    (300.0 , 400.0),
    "2026-09-18 15:30",
    1,
    {"sta03"},
    "pending"
)

event4 = Event(
    400,
    1.0,
    20.0,
    (300.0 , 400.0),
    "2026-09-18 15:30",
    1,
    {"sta04"},
    "pending"
)
event5 = Event(
    500,
    6.0,
    20.0,
    (300.0 , 400.0),
    "2026-09-18 15:30",
    1,
    {"sta05"},
    "pending"
)

event6 = Event(
    600,
    5.0,
    20.0,
    (300.0 , 400.0),
    "2026-09-18 15:30",
    1,
    {"sta06"},
    "pending"
)


tree = AVL()
tree.insert(event1)
tree.insert(event2)
tree.insert(event3)
tree.insert(event4)
tree.insert(event5)
tree.insert(event6)

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
"""

tree.delete(100)

items = tree.breadth_first()
for event in items:
    print(event)

print(" ")


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


list_historic=tree.historic()
for h in list_historic:
    print(h)
print (" ")
