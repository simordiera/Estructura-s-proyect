from scr.models.AVL import AVL
from scr.models.Event import Event


event1 = Event(
    100,
    4.0,
    20.0,
    (50.0 , 40.0),
    "2026-09-18 15:30",
    {"sta01"},
)

event2 = Event(
    200,
    4.0,
    20.0,
    (30.0 , 40.0),
    "2026-09-18 16:30",
    {"sta02"},
)
event3 = Event(
    300,
    4.5,
    20.0,
    (30.0 , 40.0),
    "2026-09-18 15:30",
    {"sta03"},
)

event4 = Event(
    400,
    4.0,
    20.0,
    (30.0 , 40.0),
    "2026-09-18 15:30",
    {"sta04"},
)
event5 = Event(
    500,
    4.0,
    20.0,
    (30.0 , 40.0),
    "2026-09-18 15:30",
    {"sta05"},
)

event6 = Event(
    600,
    4.0,
    20.0,
    (30.0 , 40.0),
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

tree.review(500) #revision de un sismo

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

event7 = Event(
    500,
    8.0,
    40.0,
    (200.0 , 0.0),
    "2026-09-18 15:30",
    {"sta07"},
    4
)

tree.insert(event7)


items = tree.breadth_first()
for event in items:
    print(event)

print(" ")

