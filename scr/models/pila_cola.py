def __init__ (self):
    self.reportes_pendientes=[]
    self.deshacer_acciones=[]

def agregar (self, tuple):
    self.reportes_pendientes.append(tuple)

def validar (self):
    longitud=len(self.reportes_pendientes)
    if (longitud==0):
        return True
    return False

def eliminar(self):
    if self.validar():
        return None
    return self.reportes_pendientes.pop(0)

def mirar_ultimo (self):
    if self.validar():
        return None
    return self.reportes_pendientes[0]


def agregar_ (self, tuple):
    self.deshacer_acciones.append(tuple)

def validar_ (self):
    longitud=len(self.deshacer_acciones)
    if (longitud==0):
        return True
    return False

def eliminar_(self):
    if self.validar_():
        return None
    return self.deshacer_acciones.pop()

def mirar_ultimo_ (self):
    if self.validar_():
        return None
    return self.deshacer_acciones[-1]
