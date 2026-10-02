from turtle import color

import streamlit as st
import pandas as pd
import plotly.express as px
import json
from scr.models.Event import Event
from scr.models.Archivo import guardar_json , cargar_json
from scr.models.AVL import AVL
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



# CARGAR LOS DATOS DEL JSON
if "data" not in st.session_state:
    try:
        st.session_state.data = cargar_json()
    except FileNotFoundError:
        st.session_state.data = []

# CREAR Y RECONSTRUIR EL AVL
if "arbol" not in st.session_state:
    st.session_state.arbol = AVL()

    for sismo in st.session_state.data:

        evento = Event(
            sismo["identificador"],
            sismo["magnitud"],
            sismo["profundidad"],
            tuple(sismo["coordenadas"]),
            f'{sismo["fecha"]}T{sismo["hora"]}',
            sismo["estación"],
            sismo["estado_atención"]
        )

        st.session_state.arbol.insert(evento)

# RECUPERAR EL ARBOL
arbol = st.session_state.arbol

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

# boton pa crear
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
                for sismo in data:
                    evento = Event(
                    sismo["identificador"],
                    sismo["magnitud"],
                    sismo["profundidad"],
                    tuple(sismo["coordenadas"]),
                    f'{sismo["fecha"]}T{sismo["hora"]}',
                    sismo["estación"],
                    sismo["estado_atención"]
        )

                    arbol.insert(evento)
                guardar_json(data)
                st.success("Archivo cargado correctamente :)")
                st.session_state.data = data
                st.write(st.session_state.data)
                st.success("Archivo cargado correctamente :)")
                #st.session_state.show_options = False
                #st.session_state.show_upload = False
                #st.rerun()

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
                    if arbol.review(id) == 1:
                        st.error("El sismo ya esta registrado")
                    else:
                        fecha_hora = f"{date}T{time}"
                        evento = Event(id,magnitude,depth,(x, y),fecha_hora,stations)
                        arbol.insert(evento)
                        st.session_state.data.append ({
                            "identificador": id,
                            "magnitud": magnitude,
                            "coordenadas": (x, y),
                            "fecha": str(date),
                            "hora": str(time),
                            "lugar_reporte": report_location,
                            "estación":stations,
                            "profundidad":depth,
                })

                        guardar_json(st.session_state.data)

                        st.session_state.show_options = False
                        st.session_state.show_form = False
                        #  st.rerun()
#cambiar de color la pag si hay mas de 10 sismos, pa que se vea mas dramatico
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
    if st.checkbox("Modo estres"):
        color_fondo = "#9c0720"
        color_texto = "#000000"
        color_fondo2 = "#610000"
        color_fondo3 = "#82303C"
        color_boton = "#734141"
        color_boton_texto = "#000000"
        color_fondo_pameter = "#352F30"
        color_texto_pameter = "#FFFFFF"
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
    }}
    </style>
    """,
    unsafe_allow_html=True
)

#BOTON PA ELIMINAR
if "show_delete" not in st.session_state:
    st.session_state.show_delete = False
if st.button("Eliminar sismo"):
    st.session_state.show_delete = True
if st.session_state.get("show_delete", False):
    id=st.number_input("ingrese el numero identificador del sismo que desea eliminar", step=1, min_value=1, max_value=999999, key="delete_id_input")
    if st.button("eliminar definitivamente"):
        result=arbol.delete(id)
        if result is None:
            st.write("No se encontró ningún sismo con ese ID.")
        else:
            st.write("Se eliminó el sismo con ID:", result.value.get_id())
            st.session_state.data = [
            sismo for sismo in st.session_state.data
            if sismo["identificador"] != id
    ]

            guardar_json(st.session_state.data)

    cerrar=st.checkbox("cerrar busqueda", key="close_delete_search")
    if cerrar:
        st.session_state.show_delete = False
        st.rerun()

#BOTON QUE CONTIENE OTRO BOTON
if st.button("Buscar por id"):
    st.session_state.show_search = True

#BOTON QUE CONTIENE EL COSO DE REVISAR SI EL METODO ESTA O NO
if st.session_state.get("show_search", False):
    id=st.number_input("ingrese el numero identificador del sismo que desea buscar", step=1, min_value=1, max_value=999999, key="search_id_input")
    if st.button("esta el sismo?"):
        st.write(arbol.root)
        result= arbol.review(id)
        if result==1:
            st.write("Esta en el arbol")
        else:
            st.write("no esta en el arbol")
    cerrar=st.checkbox("cerrar busqueda", key="close_search")
    if cerrar:
        st.session_state.show_search = False
        st.rerun()

#boton pa revisar si el sismo esta revisado o no
if "show_review" not in st.session_state:
    st.session_state.show_review = False
if st.button("Sismo revisado o no"):
    st.session_state.show_review = True
if st.session_state.get("show_review", False):
    id=st.number_input("ingrese el numero identificador del sismo que desea buscar", step=1, min_value=1, max_value=999999, key="review_id_input")
    if st.button("revisar"):
        sismo=arbol.research(id)
        if sismo is None:
            st.warning("No se encontró ningún sismo con ese ID.")
        cerrar=st.checkbox("cerrar busqueda", key="close_review_search")
        if cerrar:
            st.session_state.show_review = False
            st.rerun()

#boton pa corregir un sismito
if "show_correct" not in st.session_state:
    st.session_state.show_correct = False
if st.button("Corregir un sismo"):
    st.session_state.show_correct = True
if st.session_state.get("show_correct", False):
    id=st.number_input("ingrese el numero identificador del sismo que desea corregir", step=1, min_value=1, max_value=999999, key="correct_id_input")
    if st.button("buscar"):
        sismo=arbol.research(id)
        if sismo is None:
            st.warning ("No se encontró ningún sismo con ese ID.")
        else:
            if st.button("Corregir"):
                st.selectbox(f"¿Qué desea corregir del sismo con ID: {id}?", options=["Prioridad", "Magnitud", "Profundidad", "Coordenada x" , "coordenada y", "Fecha" , "hora", "Estación", "Estado de atención"])
        cerrar=st.checkbox("cerrar busqueda", key="close_correct_search")
        if cerrar:
            st.session_state.show_correct = False
            st.rerun()

#checkbox pa altura de nodo que busque
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
            st.write(f"ID: {sismo.get_id()}, Altura: {height}")
        cerrar=st.checkbox("cerrar busqueda", key="close_height_search")
        if cerrar:
            st.session_state.show_height = False
            st.rerun()

#checbox pa nivel de nodo
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
            level=sismo.level
            st.write("Nivel del nodo:")
            st.write(f"ID: {sismo.get_id()}, Nivel: {level}")
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
            "lat": sismo["coordenadas"][1],
            "lon": sismo["coordenadas"][0],
            "identificador": sismo["identificador"],
            "magnitud": sismo["magnitud"],
            "fecha": sismo["fecha"],
            "hora": sismo["hora"],
            "lugar_reporte": sismo["lugar_reporte"]
        })
    data = pd.DataFrame(datos_mapa)

    # tamaño pa los puntos (que tan grandes son), tiene que ser positivo
    data["tamaño"] = data["magnitud"].abs() + 1

    fig = px.scatter_geo(
        data,
        lat="lat",
        lon="lon",

        # Nombre que aparece al pasar el mouse
        hover_name="lugar_reporte",
        # Nombre que aparece directamente sobre el punto
        text="lugar_reporte",
        # El tamaño depende de la magnitud
        size="tamaño",
        #el color  dependiendo de la magnitud del sismo, mientras mas grande el numero, mas azul es
        color="magnitud",
        hover_data={
            "identificador": True,
            "magnitud": True,
            "fecha": True,
            "hora": True,
            "lat": True,
            "lon": True,
            "tamaño": False
        },

        size_max=100,
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
    mapbox=dict(
        center=dict(lat=4.6243, lon=-74.0636),  # Reemplaza con las coordenadas de tu mapa
        zoom=10                          # Ajusta el nivel de zoom (0 a 20)
    )

else:

    st.write("No hay sismos para mostrar en el mapa.")