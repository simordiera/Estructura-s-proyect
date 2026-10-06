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
import inspect
# Main Streamlit page.

# Configure the page layout.
st.set_page_config(
    page_title="SismoLab", #Page name
    page_icon= ":leaves:", #Page icon
    layout="wide",  #distribution of elements
    initial_sidebar_state="expanded", #so that the sidebar appears open from the start
)

st.title("SismoLab", text_alignment="center")

#`session_state` is used to store information; it is utilized with buttons to open and close elements—especially when dealing with nested buttons.
if "show_options" not in st.session_state:
    st.session_state.show_options = False 
if "show_form" not in st.session_state:
    st.session_state.show_form = False
if "show_search" not in st.session_state:
    st.session_state.show_search = False
if "show_upload" not in st.session_state:
    st.session_state.show_upload = False
if "modo_estres" not in st.session_state:
    st.session_state["modo_estres"] = False

# Change the stress mode according to the checkbox state.
def cambiar_theme(): 
    # Save the current checkbox value as the application's stress mode state.
    st.session_state["modo_estres"] = st.session_state["stress_checkbox"]
    if "arbol" in st.session_state:
        # Enable or disable AVL balancing according to the selected stress mode
        st.session_state.arbol.stress_mode(
            st.session_state["modo_estres"])
# Initialize the stress mode checkbox with the current stress mode value.
if "stress_checkbox" not in st.session_state:
    st.session_state["stress_checkbox"] = st.session_state["modo_estres"] # Keep the checkbox synchronized with the stored stress mode.

# Create a new empty Binary Search Tree.
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
        # Insert the created event into the Binary Search Tree.
        nuevo_bst.insert(evento)

    return nuevo_bst
# Load data from JSON.
if "data" not in st.session_state:
        st.session_state.data = cargar_json()

if "arbol_bst" not in st.session_state:
    st.session_state.arbol_bst = reconstruir_bst(st.session_state.data) 

# Create or rebuild the AVL.
if "arbol" not in st.session_state or len(st.session_state.arbol.in_order() or []) == 0:
    st.session_state.arbol = AVL( stress_mode=st.session_state["modo_estres"])

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

# Restore the active tree state.
arbol = st.session_state.arbol
arbol_bst = st.session_state.arbol_bst
arbol.stress_mode(st.session_state["modo_estres"])
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

st.session_state.scenario.attach_trees(
    st.session_state.arbol,
    st.session_state.arbol_bst,
)
st.session_state.scenario.sync_comparison_tree()
st.session_state.arbol_bst = st.session_state.scenario.bst

# Display the main information.
recorrido = arbol.in_order()
# Markdown enables page styles and formatted HTML, button style 
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
""", unsafe_allow_html=True) #If `unsafe` isn't there, the Markdown doesn't work.


st.subheader("Bienvenido a SismoLab, aquí puedes registrar y analizar sismos de manera eficiente y visual.", text_alignment="center")
# Create-event controls.
st.write("Si deseas crear un nuevo registro de sismos, presiona el botón 'crear'.")
if st.button("crear"):
    st.session_state.show_options = True
# Show the upload and manual-entry options.
if st.session_state.show_options:
    # Place the two input options side by side.
    col1, col2 = st.columns(2)

    # Open the JSON upload control.
    with col1:
        if st.button("Subir archivo JSON"):
            st.session_state.show_upload = True

        if st.session_state.show_upload:
            uploaded_file = st.file_uploader("Puedes subir tu archivo aquí! :)",
            type=["json"]
            ) #how to upload a JSON

            if uploaded_file is not None:
                data = json.load(uploaded_file)
                st.session_state.data = data
                guardar_json(st.session_state.data)
                # REBUILD AVL
                st.session_state.arbol = AVL( stress_mode=st.session_state["modo_estres"])

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
                st.session_state.scenario.attach_trees(
                    st.session_state.arbol,
                    st.session_state.arbol_bst,
                )
                st.success("Archivo cargado correctamente :)")
                st.session_state.show_upload=False
                # Keep these controls open until the rerun completes.
                st.rerun()

    # Open the manual-entry form.
    with col2:
        if st.button("Llenar datos manualmente"):
            st.session_state.show_form = True
        if st.session_state.show_form:
            #data entry form
            with st.form("my_form"):
                st.title("LLena la información del sismo :)")
                id = st.number_input("ingrese el identificador",step=1,min_value=1,max_value=999999, key="id_input", value=None,placeholder="identificador...")
                magnitude = st.number_input("ingrese la magnitud",min_value=-2.0,max_value=10.0,step=0.1, value=None,placeholder="magnitud...")
                depth = st.number_input("ingrese la profundidad",min_value=0.0,max_value=700.0,step=0.1, value=None, placeholder="profundidad...")
                x = st.number_input("coordenada X",min_value=0,max_value=1000,value=None, placeholder="coordenada..." )
                y = st.number_input("coordenada Y", min_value=0,  max_value=1000, value=None, placeholder="cordenada...")
                date = st.date_input("fecha", max_value=pd.Timestamp.now().date())
                time = st.time_input("hora")
                stations = st.text_input("estaciones", value=None, placeholder="estacion...")
                report_location = st.text_input("lugar del reporte", value=None, placeholder="lugar...")
                submitted = st.form_submit_button("Subir archivo") #upload form 

                if submitted:
                    if arbol.research(id) is not None:
                        st.error("El sismo ya esta registrado") #If the ID was already there, say so.
                    else:
                        fecha_hora = f"{date}T{time}"
                        evento = Event(id,magnitude,depth,(x, y),fecha_hora,stations)
                        
                        arbol.insert(evento)
                        st.session_state.scenario.sync_comparison_tree()
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
                        st.session_state.scenario.attach_trees(
                            st.session_state.arbol,
                            st.session_state.arbol_bst,
                        )
                        st.session_state.show_options = False
                        st.session_state.show_form = False
                        st.rerun()
#cambiar de color la pag si hay mas de 10 sismos, pa que se vea mas dramatico
#stress mode
with st.sidebar:
    st.title("seleccione aquí para el activar el modo estres")
    color_fondo="000000" #They have to be placed here to initialize the variables.
    color_texto="000000"
    color_fondo2="000000"
    color_fondo3="000000"
    color_boton="000000"
    color_boton_texto="000000"
    color_fondo_pameter="000000"
    color_texto_pameter="000000"
    color_fondo_ar="000000"
    color_arriba="000000"
    st.checkbox("Modo estres", key="stress_checkbox", on_change=cambiar_theme) #checkbox
    if st.session_state["modo_estres"]: #Stress mode colors
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
        st.image("scr/pages/resources/estres.jpg", width=300) #sidebar  img
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
) #html, stress mode

# Burst-report mode.
if "modo_rafaga" not in st.session_state:
    st.session_state["modo_rafaga"] = False
def cambiar_theme(): 
    st.session_state["modo_rafaga"] = st.session_state["rg_checkbox"] 
if "rg_checkbox" not in st.session_state:
    st.session_state["rg_checkbox"] = st.session_state["modo_rafaga"]
with st.sidebar:
    st.title("seleccione aquí para el activar el modo rafaga")
    color_fondo="000000"
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

# Delete-event controls.
st.write("Si deseas eliminar un registro de sismos, presiona el botón 'Eliminar sismo'.")
if "show_delete" not in st.session_state:
    st.session_state.show_delete = False
if st.button("Eliminar sismo"):
    st.session_state.show_delete = True
if st.session_state.get("show_delete", False):
    id=st.number_input("ingrese el numero identificador del sismo que desea eliminar", step=1, min_value=1, max_value=999999, key="delete_id_input", placeholder="identificador...")
    if st.button("eliminar definitivamente"):
        result=arbol.delete(id) 
        if result is None:
            st.write("No se encontró ningún sismo con ese ID.")
        else:
            st.write("Se eliminó el sismo correctamente")
            st.session_state.data = [
            sismo for sismo in st.session_state.data
            if sismo["id"] != id #If the earthquake exists, delete it; otherwise, state that it does not exist.
    ]

            guardar_json(st.session_state.data)
            st.session_state.scenario.sync_comparison_tree()
            st.session_state.arbol_bst = st.session_state.scenario.bst

    cerrar=st.checkbox("cerrar busqueda", key="close_delete_search")
    if cerrar:
        st.session_state.show_delete = False
        st.rerun() #checkbox to conclude

# Search controls.
st.write("Boton para buscar un sismo por su ID.")
if st.button("Buscar por id"):
    st.session_state.show_search = True

# Search by identifier.
if st.session_state.get("show_search", False):
    id=st.number_input("ingrese el numero identificador del sismo que desea buscar", step=1, min_value=1, max_value=999999, key="search_id_input", placeholder="identificador...")
    if st.button("esta el sismo?"):
        result= arbol.research(id)
        if result is not None:
            st.write("Esta en el arbol")
        else:
            st.write("no esta en el arbol")
    cerrar=st.checkbox("cerrar busqueda", key="close_search")
    if cerrar:
        st.session_state.show_search = False
        st.rerun()

# Review controls.
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
    # Check the review status.
    if st.session_state.get("show_check_review", False):
        id = st.number_input("ingrese el numero identificador del sismo que desea buscar",step=1,min_value=1,max_value=999999,key="review_id_input", placeholder="identificador...")
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
    # Mark the event as reviewed.
    if st.session_state.get("show_do_review", False):
        id = st.number_input("ingrese el numero identificador del sismo que desea revisar",step=1,min_value=1,max_value=999999,key="do_review_id_input", placeholder="Identificador...")
        if st.button("Revisar sismo", key="do_review_button"):
            resultado = arbol.review(id)
            if resultado:
                sismo = arbol.research(id)
                for sismo_json in st.session_state.data:
                    if sismo_json["id"] == id:
                        sismo_json["revisions"] = sismo.value.get_revisions()
                        break
                guardar_json(st.session_state.data)
                st.session_state.scenario.sync_comparison_tree()
                st.session_state.arbol_bst = st.session_state.scenario.bst
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
                st.write("El sismo con ID:", resultado.value.get_id(), "ha sido revisado.") #return earthquake information
    cerrar = st.checkbox("cerrar revision",key="close_review_search")
    if cerrar:
        st.session_state.show_review = False
        st.session_state.show_check_review = False
        st.session_state.show_do_review = False
        st.rerun()
# Correction controls.
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
        new_sismo = st.number_input("Ingrese la nueva magnitud",min_value=-2.0,max_value=10.0,step=0.1,key="new_magnitude_input", value=None, placeholder="magnitud...")
    elif opcion == "Profundidad":
        new_sismo = st.number_input("Ingrese la nueva profundidad",min_value=0.0,max_value=700.0,step=0.1,key="new_depth_input", value=None, placeholder="profundidad...")
    elif opcion == "Coordenada x":
        new_sismo = st.number_input("Ingrese la nueva coordenada x",min_value=0,max_value=1000,step=1,key="new_x_input", value=None, placeholder="coordenada...")
    elif opcion == "Coordenada y":
        new_sismo = st.number_input("Ingrese la nueva coordenada y",min_value=0,max_value=1000,step=1,key="new_y_input", value=None, placeholder="coordenada...")
    elif opcion == "Fecha":
        new_sismo = st.date_input("Ingrese la nueva fecha",max_value=pd.Timestamp.now().date(),key="new_date_input")
    elif opcion == "hora":
        new_sismo = st.time_input("Ingrese la nueva hora",key="new_time_input")
    elif opcion == "Estación":
        new_station = st.text_input("Ingrese la nueva estación",key="new_station_input", value=None, placeholder="estacion...")
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
            st.session_state.scenario.attach_trees(
                st.session_state.arbol,
                st.session_state.arbol_bst,
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

# Node-height query.
st.write("encontrar la altura de un sismo.")
if "show_height" not in st.session_state:
    st.session_state.show_height = False
if st.button("Altura del nodo"):
    st.session_state.show_height = True
if st.session_state.get("show_height", False):
    id=st.number_input("ingrese el numero identificador del sismo que desea buscar", step=1, min_value=1, max_value=999999, key="height_id_input", value=None, placeholder="identificador...")
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

# Node-level query.
st.write("encontrar el nivel de un sismo.")
if "show_level" not in st.session_state:
    st.session_state.show_level = False
if st.button("Nivel del nodo"):
    st.session_state.show_level = True
if st.session_state.get("show_level", False):
    id=st.number_input("ingrese el numero identificador del sismo que desea buscar", step=1, min_value=1, max_value=999999, key="level_id_input", value=None, placeholder="identificador...")
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

# Access-budget query.
st.write("consultar el presupuesto de acceso de un sismo.")
if "show_budget" not in st.session_state:
    st.session_state.show_budget = False
if st.button("Presupuesto de acceso"):
    st.session_state.show_budget = True
if st.session_state.get("show_budget", False):
    budget_id = st.number_input(
        "ingrese el numero identificador del sismo que desea buscar",
        step=1,
        min_value=1,
        max_value=999999,
        key="budget_id_input",
    )
    budget_limit = st.number_input(
        "ingrese el límite de nivel permitido",
        min_value=0,
        step=1,
        key="budget_limit_input",
    )
    if st.button("Consultar presupuesto", key="budget_button"):
        sismo = arbol.research(budget_id)
        if sismo is None:
            st.warning("No se encontró ningún sismo con ese ID.")
        else:
            level = arbol.node_level(budget_id)
            result = arbol.budget(budget_limit, budget_id)
            st.write("Presupuesto de acceso:")
            st.write(
                f"ID: {sismo.value.get_id()}, "
                f"Nivel: {level}, Límite: {budget_limit}"
            )
            st.success(result.capitalize())
    cerrar = st.checkbox("cerrar presupuesto", key="close_budget_search")
    if cerrar:
        st.session_state.show_budget = False
        st.rerun()


# Navigation hint.
st.sidebar.success('Aqui puedes navegar a las diferentes paginas del proyecto')

# Event map.
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

    # Use a positive marker size for every magnitude.
    data["tamaño"] = data["magnitude"].abs() + 1

    fig = px.scatter_geo(
        data,
        lat="lat",
        lon="lon",

        # Label shown on hover.
        hover_name="station",
        # Label shown next to the point.
        text="station",
        # Marker size follows magnitude.
        size="tamaño",
        # Color intensity follows magnitude.
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
    #map design
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

#show earthquakes that were removed
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
            ) #html
else:
    st.info("No hay sismos eliminados.")

#search for earthquake aftershocks by ID
st.markdown("""
    <div style="
        background-color: #F0FDFA;
        padding: 22px;
        border-radius: 15px;
        border-left: 6px solid #00BFA6;
        margin-bottom: 15px;
    ">
        <h3 style="color: #1B4332; margin: 0;">
            Busqueda de réplicas
        </h3>
        <p style="color: #386641; margin-bottom: 0;">
            Ingrese el id del sismo para encontrar las posibles réplicas.
        </p>
    </div>
""", unsafe_allow_html=True) #html
id_referencia = st.number_input(
    "Escriba el id del sismo", min_value=1,max_value=999999,step=1,value=None,placeholder="id del sismo del sismo...")
if id_referencia is not None:
    replicas = st.session_state.arbol.compare(int(id_referencia))
    if replicas is None:
        replicas = []
    if replicas:
        st.success(f"Se encontraron {len(replicas)} posibles réplicas.")
        datos_replicas = []
        for replica in replicas:
            sismo = replica.value
            datos_replicas.append({
                "id": sismo.get_id(),
                "magnitude": sismo.get_magnitude(),
                "depth": sismo.get_depth(),
                "epicenter": str(sismo.get_epicenter()),
                "datetime": str(sismo.get_datetime()),
                "station": sismo.get_station()
            })

        st.dataframe(datos_replicas,use_container_width=True,hide_index=True)
    else:
        st.info(
            "No se encontraron réplicas para ese ID. ")

#clock
st.title("Reloj")
if "simulation_clock" not in st.session_state:
    st.session_state.simulation_clock = datetime.now()

if "clock_real_start" not in st.session_state:
    st.session_state.clock_real_start = datetime.now()

if "clock_sim_start" not in st.session_state:
    st.session_state.clock_sim_start = st.session_state.simulation_clock


@st.fragment(run_every="1s") #show the progress per second
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

    with col1: #set the clock forward one hour
        if st.button("+ 1 hora"):
            st.session_state.simulation_clock += timedelta(hours=1)
            st.session_state.clock_sim_start = st.session_state.simulation_clock
            st.session_state.clock_real_start = datetime.now()

    with col2: #move up by a day
        if st.button("+ 1 día"):
            st.session_state.simulation_clock += timedelta(days=1)
            st.session_state.clock_sim_start = st.session_state.simulation_clock
            st.session_state.clock_real_start = datetime.now()

    with col3: #move up by a week
        if st.button("+ 1 semana"):
            st.session_state.simulation_clock += timedelta(weeks=1)
            st.session_state.clock_sim_start = st.session_state.simulation_clock
            st.session_state.clock_real_start = datetime.now()


reloj()