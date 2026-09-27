import sys
from pathlib import Path

import streamlit as st


MODELS_PATH = Path(__file__).resolve().parents[1] / "scr" / "models"
if str(MODELS_PATH) not in sys.path:
    sys.path.insert(0, str(MODELS_PATH))

from BST import BST
from Event import Event


st.title("Visualización del árbol BST")
st.caption("Comparación del árbol BST del proyecto SismoLab con la clave (prioridad, magnitud, identificador).")


def create_example_events():
    examples = [
        (100, 2.0, 20.0, (300.0, 400.0), "2026-09-18 15:30", "sta01"),
        (200, 2.0, 20.0, (300.0, 400.0), "2026-09-18 16:30", "sta02"),
        (300, 2.0, 20.0, (300.0, 400.0), "2026-09-18 15:30", "sta03"),
        (400, 2.0, 20.0, (300.0, 400.0), "2026-09-18 15:30", "sta04"),
        (500, 2.0, 20.0, (300.0, 400.0), "2026-09-18 15:30", "sta05"),
        (600, 2.0, 20.0, (300.0, 400.0), "2026-09-18 15:30", "sta06"),
        (700, 2.0, 20.0, (300.0, 400.0), "2026-09-18 17:30", "sta07"),
        (800, 2.0, 20.0, (300.0, 400.0), "2026-09-18 18:30", "sta08"),
        (900, 2.0, 20.0, (300.0, 400.0), "2026-09-18 19:30", "sta09"),
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
            lines.append(f'    {empty_id} [label="vacio", shape=point];')
            lines.append(f'    {current_id} -> {empty_id} [style=dashed];')
        else:
            lines.append(f'    {current_id} -> {dot_node_id(child)};')
            append_dot_edges(child, lines)


def tree_to_dot(tree):
    lines = [
        "digraph BST {",
        "    graph [rankdir=TB, bgcolor=\"transparent\", nodesep=0.45, ranksep=0.65];",
        "    node [shape=box, style=\"rounded,filled\", fillcolor=\"#F4EBDC\", color=\"#76552B\", fontname=\" sans-serif\"];",
        "    edge [color=\"#84745F\", arrowsize=0.7];",
    ]
    if tree.root is None:
        lines.append('    empty [label="Arbol vacio", shape=box];')
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


with st.sidebar:
    st.header("Ejemplo")
    insertion_order = st.selectbox(
        "Orden de insercion",
        ("Orden del archivo", "Clave ascendente", "Clave descendente"),
    )
    st.info("El BST conserva el orden de insercion y no aplica rotaciones ni balanceo AVL.")

events = create_example_events()
if insertion_order == "Clave ascendente":
    events.sort(key=lambda event: event.get_code())
elif insertion_order == "Clave descendente":
    events.sort(key=lambda event: event.get_code(), reverse=True)

tree = BST()
for event in events:
    tree.insert(event)

st.subheader("Arbol activo")
st.info("Este arbol muestra la estructura BST sin balanceo, para compararla con el AVL.")

left_column, right_column = st.columns([2, 1])
with left_column:
    st.graphviz_chart(tree_to_dot(tree), use_container_width=True)
with right_column:
    st.metric("Eventos activos", len(events))
    st.metric("Altura", calculated_height(tree.root))
    st.metric("Raiz", f"SIS-{tree.root.value.get_id():06d}" if tree.root else "-")
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
        st.code(" -> ".join(identifiers) if identifiers else "Arbol vacio")

st.caption("Las lineas discontinuas representan enlaces vacios. La profundidad del nodo es distinta de la profundidad del hipocentro.")
