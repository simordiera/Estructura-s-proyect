import json
from Node import Node
from AVL import AVL
from typing import Optional
from Event import Event



def save_earthquakes(earthquakes):
    with open("sismos.json", "w") as file:
        json.dumb(earthquakes, file, ident=4)

def load_earthquakes():
    with open("sismos.json", "r") as file:
        return json.load(file)


event1 = Event(
    100,
    5.0,
    20.0,
    (300.0 , 400.0),
    "2026-09-13",
    1,
    {"sta01"},
    "pending"
)

event2 = Event(
    200,
    5.0,
    20.0,
    (300.0 , 400.0),
    "2026-09-13",
    1,
    {"sta01"},
    "pending"
)
event3 = Event(
    300,
    5.0,
    20.0,
    (300.0 , 400.0),
    "2026-09-13",
    1,
    {"sta01"},
    "pending"
)

event4 = Event(
    400,
    5.0,
    20.0,
    (300.0 , 400.0),
    "2026-09-13",
    1,
    {"sta01"},
    "pending"
)
event5 = Event(
    500,
    5.0,
    20.0,
    (300.0 , 400.0),
    "2026-09-13",
    1,
    {"sta01"},
    "pending"
)

event6 = Event(
    600,
    5.0,
    20.0,
    (300.0 , 400.0),
    "2026-09-13",
    1,
    {"sta01"},
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

tree.delete(event3)

items = tree.breadth_first()
for event in items:
    print(event)

print(" ")

tree.balance()

items = tree.breadth_first()
for event in items:
    print(event)
print (" ")

