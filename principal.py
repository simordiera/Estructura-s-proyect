import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
from scr.models.Event import Event
from scr.models.Archivo import guardar_json , cargar_json, RUTA
from scr.models.AVL import AVL
from scr.models.BST import BST
from scr.models.Scenario import Scenario
from datetime import datetime, timedelta
#NO FUN IONA NADA, GAS, NO ME TOQUEN EL CODIGO

#configuracion visual de la pag
st.set_page_config(
    page_title="SismoLab",
    page_icon= ":leaves:",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("SismoLab", text_alignment="center")


if "show_options" not in st.session_state:
    st.session_state.show_options = False
if "show_form" not in st.session_state:
    st.session_state.show_form = False
if "show_search" not in st.session_state:
    st.session_state.show_search = False
if "show_upload" not in st.session_state:
    st.session_state.show_upload = False


def reconstruir_bst(data):
    nuevo_bst = BST()

    for sismo in data:
        evento = Event(
            sismo["id"],
            sismo["magnitude"],
            sismo["depth"],
            tuple(sismo["epicenter"]),
            f'{sismo["datetime"]}',
            sismo["station"],
            sismo.get("revisions", 1)
        )
        nuevo_bst.insert(evento)

    return nuevo_bst
# CARGAR LOS DATOS DEL JSON
if "data" not in st.session_state:
        st.session_state.data = cargar_json()

if "arbol_bst" not in st.session_state:
    st.session_state.arbol_bst = reconstruir_bst(st.session_state.data)

# CREAR Y RECONSTRUIR EL AVL
if "arbol" not in st.session_state or len(st.session_state.arbol.in_order() or []) == 0:
    st.session_state.arbol = AVL()

    for sismo in st.session_state.data:
        evento = Event(
            sismo["id"],
            sismo["magnitude"],
            sismo["depth"],
            tuple(sismo["epicenter"]),
            f'{sismo["datetime"]}',
            sismo["station"],
            sismo.get("revisions", 1)
        )
        st.session_state.arbol.insert(evento)

# RECUPERAR EL ARBOL
arbol = st.session_state.arbol
arbol_bst = st.session_state.arbol_bst
for id_eliminado in arbol.list_deleted:
    if arbol.research(id_eliminado) is not None:
        earthquake = arbol.research(id_eliminado)
        arbol.root = arbol._delete(
            arbol.root,
            earthquake,
            arbol.list_deleted,
            register_deleted=False
        )
if "scenario" not in st.session_state:
    st.session_state.scenario = Scenario()

st.session_state.scenario.tree = st.session_state.arbol

# MOSTRAR INFORMACIÓN
recorrido = arbol.in_order()
#Markdown sirve pa utilizar css y html, o para mostrar texto, el unsafe permite que el streamlit permita el css
st.markdown("""
<style>
div.stButton > button {
    width: 150px;
    height: 50px;
    border-radius:20px;
    font-size: 18px;
    font-weight: bold;
    background-color:#77ACA2;
    border: 2px solid white;

}
</style>
""", unsafe_allow_html=True)


st.subheader("Bienvenido a SismoLab, aquí puedes registrar y analizar sismos de manera eficiente y visual.", text_alignment="center")
# boton pa crear
st.write("Si deseas crear un nuevo registro de sismos, presiona el botón 'crear'.")
if st.button("crear"):
    st.session_state.show_options = True

# mostrar los otros dos botoncitos
if st.session_state.show_options:
    #divede ls cosas en dos columnas, para que así los botoncitos queden al lado.
    col1, col2 = st.columns(2)

    #oprimir boton para poder cargar un archivo de tipo JSON (TENGO QUE CORREGIR LO DE QUE SE CIERRA SOLO)
    with col1:
        if st.button("Subir archivo JSON"):
            st.session_state.show_upload = True

        if st.session_state.show_upload:
            uploaded_file = st.file_uploader("Puedes subir tu archivo aquí! :)",
            type=["json"]
            )

            if uploaded_file is not None:
                data = json.load(uploaded_file)
                st.session_state.data = data
                guardar_json(st.session_state.data)
                # RECONSTRUIR EL AVL
                st.session_state.arbol = AVL()

                for sismo in st.session_state.data:
                    evento = Event(
                    sismo["id"],
                    sismo["magnitude"],
                    sismo["depth"],
                    tuple(sismo["epicenter"]),
                    f'{sismo["datetime"]}',
                    sismo["station"],
                    sismo.get("revisions", 1)
                )

                    st.session_state.arbol.insert(evento)
                st.session_state.arbol_bst = reconstruir_bst(st.session_state.data)
                arbol=st.session_state.arbol
                st.success("Archivo cargado correctamente :)")
                #st.session_state.show_options = False
                #st.session_state.show_upload = False
                st.rerun()

    #segundo boton para llenar los datos manalmente(tengo que )
    with col2:
        if st.button("Llenar datos manualmente"):
            st.session_state.show_form = True
        if st.session_state.show_form:

            with st.form("my_form"):
                st.title("LLena la información del sismo :)")
                id = st.number_input("ingrese el identificador",step=1,min_value=1,max_value=999999, key="id_input")
                magnitude = st.number_input("ingrese la magnitud",min_value=-2.0,max_value=10.0,step=0.1)
                depth = st.number_input("ingrese la profundidad",min_value=0.0,max_value=700.0,step=0.1)
                x = st.number_input("coordenada X",min_value=0,max_value=1000)
                y = st.number_input("coordenada Y", min_value=0,  max_value=1000)
                date = st.date_input("fecha", max_value=pd.Timestamp.now().date())
                time = st.time_input("hora")
                stations = st.text_input("estaciones")
                report_location = st.text_input("lugar del reporte")
                submitted = st.form_submit_button("Subir archivo")

                if submitted:
                    if arbol.research(id) is not None:
                        st.error("El sismo ya esta registrado")
                    else:
                        fecha_hora = f"{date}T{time}"
                        evento = Event(id,magnitude,depth,(x, y),fecha_hora,stations)
                        
                        arbol.insert(evento)
                        st.session_state.data.append ({
                            "id": id,
                            "magnitude": magnitude,
                            "epicenter": [x, y],
                            "datetime": fecha_hora,
                            "station": stations,
                            "depth":depth,
                            "revisions": 1
                })

                        guardar_json(st.session_state.data)
                        st.session_state.arbol_bst = reconstruir_bst(st.session_state.data)
                        st.session_state.show_options = False
                        st.session_state.show_form = False
                        st.rerun()
#cambiar de color la pag si hay mas de 10 sismos, pa que se vea mas dramatico
if "modo_estres" not in st.session_state:
    st.session_state["modo_estres"] = False
def cambiar_theme(): 
    st.session_state["modo_estres"] = st.session_state["stress_checkbox"] 
if "stress_checkbox" not in st.session_state:
    st.session_state["stress_checkbox"] = st.session_state["modo_estres"]
#MODOOO ESTREEEES
with st.sidebar:
    st.title("seleccione aquí para el activar el modo estres")
    color_fondo="000000" #valores feiks para poder cambiar el color de la pag, si no se hace esto, el streamlit no deja cambiar el color de la pag
    color_texto="000000"
    color_fondo2="000000"
    color_fondo3="000000"
    color_boton="000000"
    color_boton_texto="000000"
    color_fondo_pameter="000000"
    color_texto_pameter="000000"
    color_fondo_ar="000000"
    color_arriba="000000"
    st.checkbox("Modo estres", key="stress_checkbox", on_change=cambiar_theme)
    if st.session_state["modo_estres"]:
        color_fondo = "#9c0720"
        color_texto = "#000000"
        color_fondo2 = "#610000"
        color_fondo3 = "#82303C"
        color_boton = "#734141"
        color_boton_texto = "#000000"
        color_fondo_pameter = "#352F30"
        color_texto_pameter = "#FFFFFF"
        color_fondo_ar = "#7C3131"
        color_arriba="#9c0720"
        st.image("scr/pages/resources/estres.jpg", width=300)
st.markdown(
    f"""
    <style>
    .stApp {{
        primaryColor: {color_fondo3};
        background-color: {color_fondo};
        color: {color_texto};
        [data-testid="stSidebar"] {{
        background-color: {color_fondo2};
    }}
    .stButton > button {{
        background-color: {color_boton};
        color: {color_boton_texto};
        border-radius: 20px;
        border: 2px solid white;
        font-weight: bold;
    }}

    .stButton > button:hover {{
        background-color: {color_fondo};
        color: {color_texto};
    }}
    [data-testid="stNumberInput"] input {{
        background-color: {color_fondo_pameter};
        color: {color_texto_pameter};
    
    }}
    [data-testid="stNumberInput"] button {{
    background-color: {color_boton};
    color: {color_boton_texto};
    }}
    [data-testid="stFileUploader"] {{
    background-color: {color_fondo_ar};
    }}
    [data-testid="stHeader"] {{
    background-color: {color_arriba};
    }}
    [data-testid="stFileUploaderDropzone"] {{
    background-color: {color_fondo_ar};
    border: 2px solid {color_fondo2};
    border-radius: 10px;
    }}
    [data-testid="stFileUploaderDropzone"] button {{
    background-color: {color_boton};
    color: {color_boton_texto};
    }}
}}
    </style>
    """,
    unsafe_allow_html=True
)

#MODO RAFAGA, YEI
if "modo_rafaga" not in st.session_state:
    st.session_state["modo_rafaga"] = False
def cambiar_theme(): 
    st.session_state["modo_rafaga"] = st.session_state["rg_checkbox"] 
if "rg_checkbox" not in st.session_state:
    st.session_state["rg_checkbox"] = st.session_state["modo_rafaga"]
with st.sidebar:
    st.title("seleccione aquí para el activar el modo rafaga")
    color_fondo="000000" #valores feiks para poder cambiar el color de la pag, si no se hace esto, el streamlit no deja cambiar el color de la pag
    color_texto="000000"
    color_fondo2="000000"
    color_fondo3="000000"
    color_boton="000000"
    color_boton_texto="000000"
    color_fondo_pameter="000000"
    color_texto_pameter="000000"
    color_fondo_ar="000000"
    color_arriba="000000"
    st.checkbox("Modo rafaga", key="rg_checkbox", on_change=cambiar_theme)
    if st.session_state["modo_rafaga"]:
        color_fondo = "#D8F3DC"
        color_texto = "#000000"
        color_fondo2 = "#B7E4C7"
        color_fondo3 = "#74C69D"
        color_boton = "#2D6A4F"
        color_boton_texto = "#FFFFFF"
        color_fondo_pameter = "#EAF7ED"
        color_texto_pameter = "#081C15"
        color_fondo_ar = "#B7E4C7"
        color_arriba="#D8F3DC"
        st.image("scr/pages/resources/amor.jpg", width=300)
st.markdown(
    f"""
    <style>
    .stApp {{
        primaryColor: {color_fondo3};
        background-color: {color_fondo};
        color: {color_texto};
        [data-testid="stSidebar"] {{
        background-color: {color_fondo2};
    }}
    .stButton > button {{
        background-color: {color_boton};
        color: {color_boton_texto};
        border-radius: 20px;
        border: 2px solid white;
        font-weight: bold;
    }}

    .stButton > button:hover {{
        background-color: {color_fondo};
        color: {color_texto};
    }}
    [data-testid="stNumberInput"] input {{
        background-color: {color_fondo_pameter};
        color: {color_texto_pameter};
    
    }}
    [data-testid="stNumberInput"] button {{
    background-color: {color_boton};
    color: {color_boton_texto};
    }}
    [data-testid="stFileUploader"] {{
    background-color: {color_fondo_ar};
    }}
    [data-testid="stHeader"] {{
    background-color: {color_arriba};
    }}
    [data-testid="stFileUploaderDropzone"] {{
    background-color: {color_fondo_ar};
    border: 2px solid {color_fondo2};
    border-radius: 10px;
    }}
    [data-testid="stFileUploaderDropzone"] button {{
    background-color: {color_boton};
    color: {color_boton_texto};
    }}
}}
    </style>
    """,
    unsafe_allow_html=True
)

#BOTON PA ELIMINAR
st.write("Si deseas eliminar un registro de sismos, presiona el botón 'Eliminar sismo'.")
if "show_delete" not in st.session_state:
    st.session_state.show_delete = False
if st.button("Eliminar sismo"):
    st.session_state.show_delete = True
if st.session_state.get("show_delete", False):
    id=st.number_input("ingrese el numero identificador del sismo que desea eliminar", step=1, min_value=1, max_value=999999, key="delete_id_input")
    if st.button("eliminar definitivamente"):
        st.write("IDs AVL:", [n.get_id() for n in arbol.in_order()])
        st.write("Eliminados:", arbol.list_deleted)

        result=arbol.delete(id)
        st.write("ID que intento eliminar:", id)
        st.write("Resultado delete:", result)
        st.write("IDs en data:", [s["id"] for s in st.session_state.data])
        st.write("IDs en AVL:", [n.get_id() for n in arbol.in_order()])
        if result is None:
            st.write("No se encontró ningún sismo con ese ID.")
        else:
            st.write("Se eliminó el sismo correctamente")
            st.session_state.data = [
            sismo for sismo in st.session_state.data
            if sismo["id"] != id
    ]

            guardar_json(st.session_state.data)
            st.session_state.arbol_bst = reconstruir_bst(st.session_state.data)

    cerrar=st.checkbox("cerrar busqueda", key="close_delete_search")
    if cerrar:
        st.session_state.show_delete = False
        st.rerun()

#BOTON QUE CONTIENE OTRO BOTON
st.write("Boton para buscar un sismo por su ID.")
if st.button("Buscar por id"):
    st.session_state.show_search = True

#BOTON QUE CONTIENE EL COSO DE buscar SI EL METODO ESTA O NO
if st.session_state.get("show_search", False):
    id=st.number_input("ingrese el numero identificador del sismo que desea buscar", step=1, min_value=1, max_value=999999, key="search_id_input")
    if st.button("esta el sismo?"):
        st.write(arbol.root)
        result= arbol.research(id)
        if result is not None:
            st.write("Esta en el arbol")
        else:
            st.write("no esta en el arbol")
    cerrar=st.checkbox("cerrar busqueda", key="close_search")
    if cerrar:
        st.session_state.show_search = False
        st.rerun()

#cosillo pa revision definitivo
st.write("revisar un sismo o ver si esta revisado")
if "show_review" not in st.session_state:
    st.session_state.show_review = False
if "show_check_review" not in st.session_state:
    st.session_state.show_check_review = False
if "show_do_review" not in st.session_state:
    st.session_state.show_do_review = False
if st.button("Revisión"):
    st.session_state.show_review = True
if st.session_state.get("show_review", False):
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Ver si está revisado"):
            st.session_state.show_check_review = True
            st.session_state.show_do_review = False
    with col2:
        if st.button("Revisar sismo"):
            st.session_state.show_do_review = True
            st.session_state.show_check_review = False
    # VER SI EL SISMO ESTÁ REVISADO
    if st.session_state.get("show_check_review", False):
        id = st.number_input("ingrese el numero identificador del sismo que desea buscar",step=1,min_value=1,max_value=999999,key="review_id_input")
        if st.button("revisar", key="check_review_button"):
            sismo = arbol.research(id)
            if sismo is None:
                st.warning("No se encontró ningún sismo con ese ID.")
            else:
                review = sismo.value.get_review()
                if review == 0:
                    st.write("El sismo con ID:",sismo.value.get_id(),"no ha sido revisado.")
                else:
                    st.write("El sismo con ID:",sismo.value.get_id(),"ya ha sido revisado.")
    # REVISAR EL SISMO
    if st.session_state.get("show_do_review", False):
        id = st.number_input("ingrese el numero identificador del sismo que desea revisar",step=1,min_value=1,max_value=999999,key="do_review_id_input")
        if st.button("Revisar sismo", key="do_review_button"):
            resultado = arbol.review(id)
            if resultado:
                sismo = arbol.research(id)
                for sismo_json in st.session_state.data:
                    if sismo_json["id"] == id:
                        sismo_json["revisions"] = sismo.value.get_revisions()
                        break
                guardar_json(st.session_state.data)
                st.session_state.arbol_bst = reconstruir_bst(st.session_state.data)
            if resultado is None:
                st.warning("No se encontró ningún sismo con ese ID.")
            else:
                st.write("ID:", resultado.value.get_id())
                st.write("hora:", resultado.value.get_datetime())
                st.write("revisiones:", resultado.value.get_revisions())
                st.write("coordenadas:", resultado.value.get_epicenter())
                st.write("estación:", resultado.value.get_station())
                st.write("profundidad:", resultado.value.get_depth())
                st.write("magnitud:", resultado.value.get_magnitude())
                st.write("El sismo con ID:", resultado.value.get_id(), "ha sido revisado.")
    cerrar = st.checkbox("cerrar revision",key="close_review_search")
    if cerrar:
        st.session_state.show_review = False
        st.session_state.show_check_review = False
        st.session_state.show_do_review = False
        st.rerun()
#boton pa corregir un sismito
st.write("corregir un sismo")
if "show_correct" not in st.session_state:
    st.session_state.show_correct = False
if "show_correct_2" not in st.session_state:
    st.session_state.show_correct_2 = False
if "sismo_encontrado" not in st.session_state:
    st.session_state.sismo_encontrado = False
if st.button("Corregir un sismo"):
    st.session_state.show_correct = True
    st.session_state.show_correct_2 = False
    st.session_state.sismo_encontrado = False
if st.session_state.show_correct:
    id = st.number_input("Ingrese el número identificador del sismo que desea corregir",step=1,min_value=1,max_value=999999,key="correct_id_input")
    sismo = arbol.research(id)
    if sismo is None:
        st.warning("No se encontró ningún sismo con ese ID.")
        st.session_state.sismo_encontrado = False
    else:
        st.session_state.sismo_encontrado = True
        if st.button("Corregir"):
            st.session_state.show_correct_2 = True
if st.session_state.show_correct_2:
    opcion = st.selectbox(
        f"¿Qué desea corregir del sismo con ID: {id}?",
        options=["Magnitud","Profundidad","Coordenada x","Coordenada y","Fecha","hora","Estación"])
    if opcion == "Magnitud":
        new_sismo = st.number_input("Ingrese la nueva magnitud",min_value=-2.0,max_value=10.0,step=0.1,key="new_magnitude_input")
    elif opcion == "Profundidad":
        new_sismo = st.number_input("Ingrese la nueva profundidad",min_value=0.0,max_value=700.0,step=0.1,key="new_depth_input")
    elif opcion == "Coordenada x":
        new_sismo = st.number_input("Ingrese la nueva coordenada x",min_value=0,max_value=1000,step=1,key="new_x_input")
    elif opcion == "Coordenada y":
        new_sismo = st.number_input("Ingrese la nueva coordenada y",min_value=0,max_value=1000,step=1,key="new_y_input")
    elif opcion == "Fecha":
        new_sismo = st.date_input("Ingrese la nueva fecha",max_value=pd.Timestamp.now().date(),key="new_date_input")
    elif opcion == "hora":
        new_sismo = st.time_input("Ingrese la nueva hora",key="new_time_input")
    elif opcion == "Estación":
        new_station = st.text_input("Ingrese la nueva estación",key="new_station_input")
    if st.button("Corregir definitivamente"):
        sismo_json_actual = next(
            s for s in st.session_state.data
            if s["id"] == id
        )
        if opcion == "Magnitud":
            new_info = {"magnitude": new_sismo}
        elif opcion == "Profundidad":
            new_info = {"depth": new_sismo}
        elif opcion == "Coordenada x":
            new_info = {"epicenter": (new_sismo,sismo_json_actual["epicenter"][1])}
        elif opcion == "Coordenada y":
            new_info = {"epicenter": (sismo_json_actual["epicenter"][0],new_sismo)}
        elif opcion == "Fecha":
            new_info = {"datetime": f"{new_sismo}T{sismo_json_actual['datetime'].split('T')[1]}"}
        elif opcion == "hora":
            new_info = {"datetime": f"{sismo_json_actual['datetime'].split('T')[0]}T{new_sismo}"}
        elif opcion == "Estación":
            new_info = {"station": new_station}
        new = arbol.data_correction(id, new_info)
        if new is not None:
            sismo = arbol.research(id)
            sismo.value.set_review(0)
            for sismo_json in st.session_state.data:
                if sismo_json["id"] == id:
                    if opcion == "Magnitud":
                        sismo_json["magnitude"] = new_sismo
                    elif opcion == "Profundidad":
                        sismo_json["depth"] = new_sismo
                    elif opcion == "Coordenada x":
                        sismo_json["epicenter"][0] = new_sismo
                    elif opcion == "Coordenada y":
                        sismo_json["epicenter"][1] = new_sismo
                    elif opcion == "Fecha":
                        sismo_json["datetime"] = f"{new_sismo}T{sismo_json['datetime'].split('T')[1]}"
                    elif opcion == "hora":
                        sismo_json["datetime"] = f"{sismo_json['datetime'].split('T')[0]}T{new_sismo}"
                    elif opcion == "Estación":
                        sismo_json["station"] = new_station
                    break
            guardar_json(st.session_state.data)
            st.session_state.arbol_bst = reconstruir_bst(
                st.session_state.data
            )
            st.success("¡Sismo corregido correctamente!")
            st.session_state.show_correct = False
            st.session_state.show_correct_2 = False
            st.session_state.sismo_encontrado = False
            st.rerun()
        else:
            st.warning("No se pudo corregir el sismo.")
if st.session_state.show_correct:
    cerrar = st.checkbox("Cerrar búsqueda",key="close_correct_search")
    if cerrar:
        st.session_state.show_correct = False
        st.session_state.show_correct_2 = False
        st.session_state.sismo_encontrado = False
        st.rerun()

#botoncito pa altura de nodo que busque
st.write("encontrar la altura de un sismo.")
if "show_height" not in st.session_state:
    st.session_state.show_height = False
if st.button("Altura del nodo"):
    st.session_state.show_height = True
if st.session_state.get("show_height", False):
    id=st.number_input("ingrese el numero identificador del sismo que desea buscar", step=1, min_value=1, max_value=999999, key="height_id_input")
    if st.button("altura"):
        sismo=arbol.research(id)
        if sismo is None:
            st.warning("No se encontró ningún sismo con ese ID.")
        else:
            height=sismo.height
            st.write("Altura del nodo:")
            st.write(f"ID: {sismo.value.get_id()}, Altura: {height}")
        cerrar=st.checkbox("cerrar busqueda", key="close_height_search")
        if cerrar:
            st.session_state.show_height = False
            st.rerun()

#botoncito pa nivel de nodo
st.write("encontrar el nivel de un sismo.")
if "show_level" not in st.session_state:
    st.session_state.show_level = False
if st.button("Nivel del nodo"):
    st.session_state.show_level = True
if st.session_state.get("show_level", False):
    id=st.number_input("ingrese el numero identificador del sismo que desea buscar", step=1, min_value=1, max_value=999999, key="level_id_input")
    if st.button("nivel"):
        sismo=arbol.research(id)
        if sismo is None:
            st.warning("No se encontró ningún sismo con ese ID.")
        else:
            level=arbol.node_level(id)
            st.write("Nivel del nodo:")
            st.write(f"ID: {sismo.value.get_id()}, Nivel: {level}")
    cerrar=st.checkbox("cerrar busqueda", key="close_level_search")
    if cerrar:
        st.session_state.show_level = False
        st.rerun()


#aparece en el menu cuando se meten en la pag prin
st.sidebar.success('Aqui puedes navegar a las diferentes paginas del proyecto')

#mapaaaaaa
st.header("Mapa de sismos")
st.info("Puedes hacer zoom y mover el mapa para explorar los sismos registrados. Los puntos representan la ubicación de cada sismo, y su tamaño y color reflejan la magnitud del evento.")

if "data" in st.session_state and len(st.session_state.data) > 0:

    datos_mapa = []

    for sismo in st.session_state.data:

        datos_mapa.append({
            "lat": sismo["epicenter"][1],
            "lon": sismo["epicenter"][0],
            "id": sismo["id"],
            "magnitude": sismo["magnitude"],
            "datetime": sismo["datetime"],
            "station": sismo["station"],
        })
    data = pd.DataFrame(datos_mapa)

    # tamaño pa los puntos (que tan grandes son), tiene que ser positivo
    data["tamaño"] = data["magnitude"].abs() + 1

    fig = px.scatter_geo(
        data,
        lat="lat",
        lon="lon",

        # Nombre que aparece al pasar el mouse
        hover_name="station",
        # Nombre que aparece directamente sobre el punto
        text="station",
        # El tamaño depende de la magnitud
        size="tamaño",
        #el color  dependiendo de la magnitud del sismo, mientras mas grande el numero, mas azul es
        color="magnitude",
        hover_data={
            "id": True,
            "magnitude": True,
            "datetime": True,
            "lat": True,
            "lon": True,
            "tamaño": False
        },

        size_max=10,
    )

    fig.update_geos(
        showland=True,
        landcolor="#F2F2F2",

        showocean=True,
        oceancolor="#A8B1EC",

        showcountries=True,
        countrycolor="#BDBDBD",

        showcoastlines=True,
        coastlinecolor="#999999",

        showlakes=True,
        lakecolor="#FFFFFF",

        projection_type="natural earth"
    )

    fig.update_traces(
        textposition="top center",

        textfont=dict(
            size=12
        ),

        marker={
            "line": {
                "width": 1,
                "color": "#111111"
            }
        }
    )

    fig.update_layout(
        height=600,

        margin={
            "r": 100,
            "t": 10,
            "l": 0,
            "b": 10
        },

        coloraxis_colorbar={
            "title": "Magnitud"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:

    st.write("No hay sismos para mostrar en el mapa.")

st.subheader("sismos eliminados:")
if arbol.list_deleted:
    cols = st.columns(len(arbol.list_deleted))

    for i, sismo in enumerate(arbol.list_deleted):
        with cols[i]:
            st.markdown(
                f"""
                <div style="
                    background-color: #E8F3F1;
                    padding: 15px;
                    border-radius: 15px;
                    text-align: center;
                    border: 2px solid #77ACA2;
                ">
                    <h4 style="color: #397A70;">
                        Sismo #{sismo}
                    </h4>
                </div>
                """,
                unsafe_allow_html=True
            )
else:
    st.info("No hay sismos eliminados.")

st.title("Reloj")
if "simulation_clock" not in st.session_state:
    st.session_state.simulation_clock = datetime.now()

if "clock_real_start" not in st.session_state:
    st.session_state.clock_real_start = datetime.now()

if "clock_sim_start" not in st.session_state:
    st.session_state.clock_sim_start = st.session_state.simulation_clock


@st.fragment(run_every="1s")
def reloj():

    ahora = datetime.now()

    tiempo_transcurrido = ahora - st.session_state.clock_real_start

    st.session_state.simulation_clock = (
        st.session_state.clock_sim_start + tiempo_transcurrido
    )

    st.subheader("Reloj de simulación")

    st.write(
        st.session_state.simulation_clock.strftime("%Y-%m-%d %H:%M:%S")
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("+ 1 hora"):
            st.session_state.simulation_clock += timedelta(hours=1)
            st.session_state.clock_sim_start = st.session_state.simulation_clock
            st.session_state.clock_real_start = datetime.now()

    with col2:
        if st.button("+ 1 día"):
            st.session_state.simulation_clock += timedelta(days=1)
            st.session_state.clock_sim_start = st.session_state.simulation_clock
            st.session_state.clock_real_start = datetime.now()

    with col3:
        if st.button("+ 1 semana"):
            st.session_state.simulation_clock += timedelta(weeks=1)
            st.session_state.clock_sim_start = st.session_state.simulation_clock
            st.session_state.clock_real_start = datetime.now()


reloj()