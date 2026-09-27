import json

def guardar_json(data, nombre="datos.json"):
    with open(nombre, "w", encoding="utf-8") as archivo:
        json.dump(data, archivo, indent=4, ensure_ascii=False)

def cargar_json(nombre="datos.json"):
    with open(nombre, "r", encoding="utf-8") as archivo:
        return json.load(archivo)
