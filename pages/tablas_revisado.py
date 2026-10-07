import streamlit as st
import pandas as pd
from scr.models.Archivo import cargar_json
from scr.models.AVL import AVL
from scr.models.Event import Event
from scr.models.Scenario import Scenario


def get_active_tree():
    """Return the session AVL, rebuilding it from persisted events if needed."""
    tree = st.session_state.get("arbol")
    scenario = st.session_state.get("scenario")
    scenario_tree = getattr(scenario, "tree", None)

    if scenario_tree is not None and (
        tree is None or (tree.root is None and scenario_tree.root is not None)
    ):
        tree = scenario_tree

    if tree is None or tree.root is None:
        data = st.session_state.get("data")
        if data is None:
            data = cargar_json()
        st.session_state.data = data

        tree = AVL()
        for record in data:
            event = Event(
                record["id"],
                record["magnitude"],
                record["depth"],
                tuple(record["epicenter"]),
                record["datetime"],
                record["station"],
                record.get("revisions", 1),
                review=record.get("review"),
            )
            existing = tree.research(event.get_id())
            if existing is None:
                tree.insert(event)
            else:
                tree.same_earthquake(event, existing)

    if scenario is None:
        scenario = Scenario()
    scenario.attach_trees(tree, st.session_state.get("arbol_bst"))
    st.session_state.arbol = tree
    st.session_state.scenario = scenario
    st.session_state.arbol_bst = scenario.bst
    return tree


arbol = get_active_tree()

#page color
color_fondo = "#6e9693"
color_texto = "#000000"
color_fondo2 = "#406e75"
color_fondo3 = "#FFFFFF"
color_boton = "#FFFFFF"
color_boton_texto = "#000000"
color_fondo_pameter = "#FFFFFF"
color_texto_pameter = "#000000"
color_fondo_ar = "#FFFFFF"
color_arriba="#6e9693"
#stress mode
if st.session_state.get("modo_estres", False):
    color_fondo = "#9c0720"
    color_texto = "#000000"
    color_fondo2 = "#610000"
    color_fondo3 = "#82303C"
    color_boton = "#734141"
    color_boton_texto = "#000000"
    color_fondo_pameter = "#352F30"
    color_texto_pameter = "#FFFFFF"
    color_fondo_ar = "#610000"
    color_arriba="#9c0720"
    st.sidebar.image("scr/pages/resources/estres.jpg", width=300)
#rg mode
if st.session_state.get("modo_rafaga", False):
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
    st.sidebar.image("scr/pages/resources/amor.jpg", width=300)



st.markdown(
    f"""
    <style>

    .stApp {{
        background-color: {color_fondo} !important;
        color: {color_texto} !important;
    }}

    [data-testid="stSidebar"] {{
        background-color: {color_fondo2} !important;
    }}

    [data-testid="stHeader"] {{
        background-color: {color_arriba} !important;
    }}

    </style>
    """,
    unsafe_allow_html=True
) #hmtl
st.title("Tablas revisados", text_alignment="center")

# Create empty lists to store reviewed and unreviewed earthquakes.
sismos_no_revisados = []
sismos_revisados = []

# Check if the AVL tree contains any nodes.
if arbol.root is not None:
    eventos = arbol.in_order()
    for evento in eventos:
        # Check if the earthquake has not been reviewed.
        if evento.get_review() == 0:
            # Add the earthquake information to the unreviewed list.
            sismos_no_revisados.append({
                "id": evento.get_id(),
                "Magnitude": evento.get_magnitude(),
                "depth": evento.get_depth(),
                "Fecha": evento.get_datetime().date(),
                "Hora": evento.get_datetime().time(),
                "Estación": evento.get_station(),
                "Revisiones": evento.get_revisions()
            })

        else:
            # Add the earthquake information to the reviewed list.
            sismos_revisados.append({
                "id": evento.get_id(),
                "Magnitude": evento.get_magnitude(),
                "depth": evento.get_depth(),
                "Fecha": evento.get_datetime().date(),
                "Hora": evento.get_datetime().time(),
                "Estación": evento.get_station(),
                "Revisiones": evento.get_revisions()
            })


st.subheader("tabla de los sismos revisados", text_alignment="center")
if len(sismos_revisados) > 0: # Check if there are any reviewed earthquakes.
    st.dataframe(
        pd.DataFrame(sismos_revisados),
        use_container_width=True
    )  # Convert the reviewed earthquakes into a DataFrame and display them.
else:
    st.info("No hay sismos revisados.")

st.subheader("tabla de los sismos sin revisar", text_alignment="center")

if len(sismos_no_revisados) > 0:
    st.dataframe(
        pd.DataFrame(sismos_no_revisados),
        use_container_width=True
    )
else:
    st.info("No hay sismos no revisados.")

