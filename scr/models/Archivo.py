import json
import os

RUTA = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "datos.json"
)

def guardar_json(data, nombre=RUTA):

    with open(nombre, "w", encoding="utf-8") as archivo:
        json.dump(data, archivo, indent=4, ensure_ascii=False)


def cargar_json(nombre=RUTA):

    if not os.path.exists(nombre):
        return []

    with open(nombre, "r", encoding="utf-8") as archivo:
        return json.load(archivo)