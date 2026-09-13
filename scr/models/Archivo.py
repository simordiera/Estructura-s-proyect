import json



def guardar_sismos (sismos):
    with open("sismos.json", "w") as archivo:
        json.dumb(sismos, archivo, ident=4)

def cargar_sismos():
    with open("sismos.json", "r") as archivo:
        return json.load(archivo)
