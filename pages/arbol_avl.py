from copy import deepcopy
from datetime import datetime

import streamlit as st

from scr.models.AVL import AVL
from scr.models.Event import Event
from scr.models.SubtreeArchive import SubtreeArchiveManager
from scr.models.UndoStack import UndoStack

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
        Event(identifier, magnitude, depth, epicenter, date, {station}, attention_status="Pendiente")
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


def create_tree():
    tree = AVL()
    for event in create_example_events():
        tree.insert(event)
    if not tree.stress_mode:
        tree.balance()
    return tree


# El arbol y la pila sobreviven a los reruns normales de Streamlit.
if "archive_age_hours" not in st.session_state:
    st.session_state.archive_age_hours = 72
if "stress_mode" not in st.session_state:
    st.session_state.stress_mode = False
if "avl_tree" not in st.session_state:
    st.session_state.avl_tree = create_tree()
if "avl_archiver" not in st.session_state:
    st.session_state.avl_archiver = SubtreeArchiveManager(st.session_state.avl_tree)
if "avl_undo" not in st.session_state:
    st.session_state.avl_undo = UndoStack()
if "avl_deleted_ids" not in st.session_state:
    st.session_state.avl_deleted_ids = set()
if "avl_restored_ids" not in st.session_state:
    st.session_state.avl_restored_ids = set()


with st.sidebar:
    st.header("Ejemplo")
    insertion_order = st.selectbox(
        "Orden de inserción",
        ("Orden del archivo", "Clave ascendente", "Clave descendente"),
    )
    balance_tree = st.checkbox("Aplicar balanceo AVL", value=True)
    st.session_state.stress_mode = not balance_tree
    st.session_state.archive_age_hours = st.number_input(
        "Antigüedad mínima T (horas)", min_value=1, value=72, step=1
    )
    st.session_state.avl_tree.set_simulation_clock(datetime.now())
    st.session_state.avl_tree.set_archive_age_hours(st.session_state.archive_age_hours)
    st.session_state.avl_tree.stress_mode = st.session_state.stress_mode
    archive_candidate = st.session_state.avl_archiver.find_candidate()
    if archive_candidate:
        st.info(
            f"Subárbol elegido automáticamente: raíz SIS-{archive_candidate['root_id']:06d} "
            f"({archive_candidate['size']} eventos)."
        )
    else:
        st.info("No hay un subárbol elegible para archivar.")
    if st.button("Archivar subárbol", disabled=archive_candidate is None):
        operation = st.session_state.avl_archiver.archive_subtree(
            st.session_state.avl_undo
        )
        if operation:
            st.success(
                f"Se archivaron {len(operation['ids'])} eventos: "
                f"{', '.join(f'SIS-{event_id:06d}' for event_id in sorted(operation['ids']))}."
            )
            st.rerun()
    if st.button("Deshacer última acción"):
        last_operation = st.session_state.avl_undo.peek_undo()
        undone = False
        if last_operation and last_operation.get("type") == "eliminar_evento":
            undone = st.session_state.avl_tree.undo_delete(st.session_state.avl_undo)
            if undone:
                restored_id = last_operation["event_id"]
                st.session_state.avl_deleted_ids.discard(restored_id)
                st.session_state.avl_restored_ids.add(restored_id)
        else:
            undone = st.session_state.avl_archiver.undo_last(st.session_state.avl_undo)

        if undone:
            st.success("La última acción se deshizo correctamente.")
            st.rerun()
    st.info("Los eventos de ejemplo se reconstruyen en cada cambio para evitar modificar otros estados de la aplicación.")

tree = st.session_state.avl_tree
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
            if tree.delete_active(event.get_id(), st.session_state.avl_undo):
                # La pagina BST consumira este ID y retirara el mismo evento.
                st.session_state.avl_deleted_ids.add(event.get_id())
                st.success(f"SIS-{event.get_id():06d} fue eliminado del AVL activo.")
                st.rerun()

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
        if tree.reactivate_historic(selected_historic_id, st.session_state.avl_undo):
            st.success(f"SIS-{selected_historic_id:06d} volvió al AVL como evento pendiente.")
            st.rerun()
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
