from copy import deepcopy
from datetime import datetime
from turtle import color

import streamlit as st

from scr.models.Event import Event
from scr.models.Scenario import Scenario
from scr.models.Archivo import cargar_json

st.title("Visualización del árbol AVL")
st.caption("Ejemplos del proyecto SismoLab ordenados por la clave (prioridad, magnitud, identificador).")


def create_example_events():
    examples = [
        (100, 2.0, 20.0, (30.0, 40.0), "2026-09-18 15:30", "sta01"),
        (200, 2.0, 20.0, (34.0, 40.0), "2026-09-18 16:30", "sta02"),
        (300, 2.0, 20.0, (30.0, 40.0), "2026-09-18 15:30", "sta03"),
        (400, 2.0, 20.0, (30.0, 40.0), "2026-09-18 15:30", "sta04"),
        (500, 2.0, 20.0, (30.0, 40.0), "2026-09-18 15:30", "sta05"),
        (600, 2.0, 20.0, (30.0, 40.0), "2026-09-18 15:30", "sta06"),
        (700, 2.0, 30.0, (30.0, 40.0), "2026-09-18 17:30", "sta07"),
        (800, 2.0, 45.0, (30.0, 40.0), "2026-09-18 18:30", "sta08"),
        (900, 4.8, 10.0, (30.0, 40.0), "2026-09-25 19:30", "sta09"),
    ]
    return [
        Event(identifier, magnitude, depth, epicenter, date, {station})
        for identifier, magnitude, depth, epicenter, date, station in examples
    ]


def calculated_height(node):
    if node is None:
        return -1
    return 1 + max(calculated_height(node.left), calculated_height(node.right))


def balance_factor(node):
    if node is None:
        return 0
    return calculated_height(node.left) - calculated_height(node.right)


def node_label(node):
    event = node.value
    priority, magnitude, identifier = event.get_code()
    return (
        f"SIS-{identifier:06d}\\n"
        f"K=({priority}, {magnitude:.1f}, {identifier})\\n"
        f"h={calculated_height(node)} | FB={balance_factor(node)}"
    )


def dot_node_id(node):
    return f"node_{id(node)}"


def append_dot_edges(node, lines):
    if node is None:
        return

    current_id = dot_node_id(node)
    lines.append(f'    {current_id} [label="{node_label(node)}"];')

    for child, side in ((node.left, "I"), (node.right, "D")):
        if child is None:
            empty_id = f"empty_{id(node)}_{side}"
            lines.append(f'    {empty_id} [label="∅", shape=point];')
            lines.append(f'    {current_id} -> {empty_id} [style=dashed];')
        else:
            lines.append(f'    {current_id} -> {dot_node_id(child)};')
            append_dot_edges(child, lines)


def tree_to_dot(tree):
    lines = [
        "digraph AVL {",
        "    graph [rankdir=TB, bgcolor=\"transparent\", nodesep=0.45, ranksep=0.65];",
        "    node [shape=box, style=\"rounded,filled\", fillcolor=\"#E8F1F2\", color=\"#24545A\", fontname=\" sans-serif\"];",
        "    edge [color=\"#6C7A80\", arrowsize=0.7];",
    ]
    if tree.root is None:
        lines.append('    empty [label="Árbol vacío", shape=box];')
    else:
        append_dot_edges(tree.root, lines)
    lines.append("}")
    return "\n".join(lines)


def event_rows(tree):
    rows = []

    def visit(node, depth):
        if node is None:
            return
        event = node.value
        priority, magnitude, identifier = event.get_code()
        rows.append(
            {
                "Profundidad": depth,
                "Identificador": f"SIS-{identifier:06d}",
                "Prioridad": priority,
                "Magnitud": magnitude,
                "Clave K": str(event.get_code()),
                "Altura": calculated_height(node),
                "Factor balance": balance_factor(node),
            }
        )
        visit(node.left, depth + 1)
        visit(node.right, depth + 1)

    visit(tree.root, 0)
    return rows


def format_events(events):
    return {f"SIS-{event.get_id():06d}": event for event in events}


def create_scenario():
    scenario = Scenario()
    data=cargar_json()
    for sismo in data:
        event = Event(
            sismo["identificador"],
            sismo["magnitud"],
            sismo["profundidad"],
            tuple(sismo["coordenadas"]),
            f'{sismo["fecha"]}T{sismo["hora"]}',
            sismo["estación"],
        )
        scenario.create_event(event)

    # Example data is the initial state, not a user action.
    scenario.undo_stack.undo_actions.clear()
    scenario.undo_stack.redo_actions.clear()
    scenario.tree.balance()
    return scenario


# El arbol y la pila sobreviven a los reruns normales de Streamlit.
if "archive_age_hours" not in st.session_state:
    st.session_state.archive_age_hours = 72
if "stress_mode" not in st.session_state:
    st.session_state.stress_mode = False
if "scenario" not in st.session_state:
    st.session_state.scenario = create_scenario()

scenario = st.session_state.scenario
if "arbol" in st.session_state:
    scenario.tree = st.session_state.arbol
tree = scenario.tree


with st.sidebar:
    insertion_order = "Orden del archivo"
    balance_tree = True
    st.session_state.stress_mode = False
    st.session_state.archive_age_hours = 72
    if tree.archive_age_hours != st.session_state.archive_age_hours:
        scenario.change_parameters({"T": st.session_state.archive_age_hours})
    if tree.stress_mode != st.session_state.stress_mode:
        scenario.set_stress_mode(st.session_state.stress_mode)
    archive_candidate = scenario.archive_manager.find_candidate()
    if archive_candidate:
        st.info(
            f"Subárbol elegido automáticamente: raíz SIS-{archive_candidate['root_id']:06d} "
            f"({archive_candidate['size']} eventos)."
        )
    else:
        st.info("No hay un subárbol elegible para archivar.")
    if st.button("Archivar subárbol", disabled=archive_candidate is None):
        operation = scenario.archive_subtree()
        if operation:
            st.success(
                f"Se archivaron {len(operation.event_ids)} eventos: "
                f"{', '.join(f'SIS-{event_id:06d}' for event_id in sorted(operation.event_ids))}."
            )
            st.rerun()
    if st.button("Deshacer última acción"):
        undone = scenario.undo()
        if undone is not None:
            st.success("La última acción se deshizo correctamente.")
            st.rerun()
        else:
            st.info("No hay acciones para deshacer.")
    if st.button("Rehacer última acción"):
        redone = scenario.redo()
        if redone is not None:
            st.success("La última acción se rehizo correctamente.")
            st.rerun()
        else:
            st.info("No hay acciones para rehacer.")
    st.info("Los eventos de ejemplo se reconstruyen en cada cambio para evitar modificar otros estados de la aplicación.")

events = tree.in_order() or []
if insertion_order == "Clave ascendente":
    events.sort(key=lambda event: event.get_code())
elif insertion_order == "Clave descendente":
    events.sort(key=lambda event: event.get_code(), reverse=True)

# El AVL es la fuente de cambios; el BST usa este estado para reflejar los
# mismos eventos sin copiar la topologia ni las rotaciones del AVL.
st.session_state.avl_sync_state = {
    "active_events": deepcopy(events),
    "historic_events": deepcopy(tree.list_historic),
    "retired_ids": set(tree.retired_ids),
    "associations": deepcopy(tree.associations),
    "metrics": tree.metrics.snapshot(),
    "simulation_clock": tree.simulation_clock,
    "archive_age_hours": tree.archive_age_hours,
}

st.subheader("Árbol activo")
if not balance_tree:
    st.warning("El árbol se muestra después de insertar, sin ejecutar la recuperación de balanceo.")
else:
    st.success("El balanceo se aplicó después de las inserciones del ejemplo.")

left_column, right_column = st.columns([2, 1])
with left_column:
    st.graphviz_chart(tree_to_dot(tree), use_container_width=True)
with right_column:
    st.metric("Eventos activos", len(events))
    st.metric("Altura", tree.height())
    st.metric("Raíz", f"SIS-{tree.root.value.get_id():06d}" if tree.root else "-",)
    st.metric("Hojas", sum(1 for row in event_rows(tree) if row["Altura"] == 0))

st.subheader("Detalle de nodos")
st.dataframe(event_rows(tree), use_container_width=True, hide_index=True)
st.caption("Cada botón elimina únicamente el nodo indicado del AVL activo.")
for event in events:
    node_columns = st.columns([5, 1])
    with node_columns[0]:
        st.write(f"SIS-{event.get_id():06d} | K={event.get_code()}")
    with node_columns[1]:
        if st.button("Eliminar", key=f"avl_delete_{event.get_id()}"):
            operation = scenario.delete_event(event.get_id())
            if operation is not None:
                st.success(f"SIS-{event.get_id():06d} fue eliminado del AVL activo.")
                st.rerun()
            else:
                st.error(f"No se pudo eliminar SIS-{event.get_id():06d}.")

st.subheader("Histórico")
historic_events = tree.list_historic
if historic_events:
    historic_rows = [
        {
            "Identificador": f"SIS-{event.get_id():06d}",
            "Prioridad": event.get_priority(),
            "Magnitud": event.get_magnitude(),
            "Estado": "Archivado",
        }
        for event in historic_events
    ]
    st.dataframe(historic_rows, use_container_width=True, hide_index=True)
    historic_ids = [event.get_id() for event in historic_events]
    selected_historic_id = st.selectbox("Evento histórico para reactivar", historic_ids)
    if st.button("Reactivar evento histórico"):
        st.warning(
            "La reactivación histórica todavía no tiene un método coordinador "
            "en Scenario.py y no se ejecutará directamente sobre AVL.py."
        )
else:
    st.info("No hay eventos archivados.")

st.subheader("Recorridos")
traversal_columns = st.columns(4)
traversals = (
    ("Preorden", tree.pre_order()),
    ("Inorden", tree.in_order()),
    ("Postorden", tree.post_order()),
    ("Por niveles", tree.breadth_first()),
)
for column, (title, traversal) in zip(traversal_columns, traversals):
    with column:
        identifiers = [f"SIS-{event.get_id():06d}" for event in (traversal or [])]
        st.write(f"**{title}**")
        st.code(" → ".join(identifiers) if identifiers else "Árbol vacío")

st.caption("L")
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
)