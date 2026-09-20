import sys
from pathlib import Path

import streamlit as st


MODELS_PATH = Path(__file__).resolve().parents[1] / "scr" / "models"
if str(MODELS_PATH) not in sys.path:
    sys.path.insert(0, str(MODELS_PATH))

from AVL import AVL
from Event import Event


st.set_page_config(page_title="Visualización AVL", page_icon="🌐", layout="wide")
st.title("Visualización del árbol AVL")
st.caption("Ejemplos del proyecto SismoLab ordenados por la clave (prioridad, magnitud, identificador).")


def create_example_events():
    examples = [
        (100, 4.0, 20.0, (300.0, 400.0), "2026-09-18 15:30", "sta01"),
        (200, 2.0, 20.0, (340.0, 400.0), "2026-09-18 16:30", "sta02"),
        (300, 3.0, 20.0, (300.0, 400.0), "2026-09-18 15:30", "sta03"),
        (400, 1.0, 20.0, (300.0, 400.0), "2026-09-18 15:30", "sta04"),
        (500, 6.0, 20.0, (300.0, 400.0), "2026-09-18 15:30", "sta05"),
        (600, 5.0, 20.0, (300.0, 400.0), "2026-09-18 15:30", "sta06"),
    ]
    return [
        Event(identifier, magnitude, depth, epicenter, date, 1, {station}, "pending")
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


with st.sidebar:
    st.header("Ejemplo")
    insertion_order = st.selectbox(
        "Orden de inserción",
        ("Orden del archivo", "Clave ascendente", "Clave descendente"),
    )
    balance_tree = st.checkbox("Aplicar balanceo AVL", value=True)
    st.info("Los eventos de ejemplo se reconstruyen en cada cambio para evitar modificar otros estados de la aplicación.")

events = create_example_events()
if insertion_order == "Clave ascendente":
    events.sort(key=lambda event: event.get_code())
elif insertion_order == "Clave descendente":
    events.sort(key=lambda event: event.get_code(), reverse=True)

tree = AVL()
for event in events:
    tree.insert(event)
if balance_tree:
    tree.balance()

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
    st.metric("Altura", calculated_height(tree.root))
    st.metric("Raíz", f"SIS-{tree.root.value.get_id():06d}" if tree.root else "-",)
    st.metric("Hojas", sum(1 for row in event_rows(tree) if row["Altura"] == 0))

st.subheader("Detalle de nodos")
st.dataframe(event_rows(tree), use_container_width=True, hide_index=True)

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

st.caption("Las líneas discontinuas representan enlaces vacíos. La profundidad del nodo es distinta de la profundidad del hipocentro.")
