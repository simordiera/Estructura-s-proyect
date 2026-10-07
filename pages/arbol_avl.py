from copy import deepcopy
from datetime import datetime
from turtle import color
import streamlit as st
from scr.models.Event import Event
from scr.models.Scenario import Scenario
from scr.models.Archivo import cargar_json


# Main title of the AVL tree visualization page
st.title("Visualización del árbol AVL")

# Description of how the events are organized in the AVL tree
st.caption(
    "Ejemplos del proyecto SismoLab ordenados por la clave "
    "(prioridad, magnitud, identificador)."
)


# ---------------------------------------------------------
# CREATE EXAMPLE EVENTS
# ---------------------------------------------------------

def create_example_events():
    # Example data used to create test events
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

    # Convert each tuple of data into an Event object
    return [
        Event(
            identifier,
            magnitude,
            depth,
            epicenter,
            date,
            {station}
        )
        for identifier, magnitude, depth, epicenter, date, station in examples
    ]


# ---------------------------------------------------------
# CALCULATE NODE HEIGHT
# ---------------------------------------------------------

def calculated_height(node):
    # An empty node has a height of -1
    if node is None:
        return -1

    # The height is one plus the greater height
    # between the left and right children
    return 1 + max(
        calculated_height(node.left),
        calculated_height(node.right)
    )


# ---------------------------------------------------------
# CALCULATE BALANCE FACTOR
# ---------------------------------------------------------

def balance_factor(node):
    # An empty node has a balance factor of 0
    if node is None:
        return 0

    # Calculate the difference between the left
    # subtree height and the right subtree height
    return calculated_height(node.left) - calculated_height(node.right)


# ---------------------------------------------------------
# CREATE THE NODE LABEL
# ---------------------------------------------------------

def node_label(node):
    # Get the Event stored inside the node
    event = node.value

    # Get the priority, magnitude and identifier
    # that make up the event key
    priority, magnitude, identifier = event.get_code()

    # Return the text displayed inside the node
    return (
        f"SIS-{identifier:06d}\n"
        f"K=({priority}, {magnitude:.1f}, {identifier})\n"
        f"h={calculated_height(node)} | FB={balance_factor(node)}"
    )


# ---------------------------------------------------------
# CREATE THE NODE TOOLTIP
# ---------------------------------------------------------

def node_tooltip(node):
    # Get the Event stored inside the node
    event = node.value

    # Get the values used to create the key
    priority, magnitude, identifier = event.get_code()

    # Get the event epicenter coordinates
    epicenter = event.get_epicenter()

    # Return the detailed information shown
    # when the user interacts with the node
    return (
        f"Identificador: SIS-{identifier:06d}\n"
        f"Magnitud: {event.get_magnitude():.1f}\n"
        f"Profundidad: {event.get_depth()}\n"
        f"Epicentro: ({epicenter[0]}, {epicenter[1]})\n"
        f"Fecha y hora: {event.get_datetime()}\n"
        f"Estación: {event.get_station()}\n"
        f"Zona: {event.get_zone()}\n"
        f"Prioridad: {priority}\n"
        f"Revisiones: {event.get_revisions()}\n"
        f"Revisado: {'Sí' if event.get_review() else 'No'}\n"
        f"Clave K: ({priority}, {magnitude:.1f}, {identifier})\n"
        f"Altura: {calculated_height(node)}\n"
        f"Factor de balance: {balance_factor(node)}"
    ).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


# ---------------------------------------------------------
# CREATE A UNIQUE GRAPHVIZ NODE ID
# ---------------------------------------------------------

def dot_node_id(node):
    # Generate a unique identifier for the current node
    return f"node_{id(node)}"


# ---------------------------------------------------------
# ADD TREE EDGES TO THE GRAPHVIZ STRUCTURE
# ---------------------------------------------------------

def append_dot_edges(node, lines):
    # Stop if the current node does not exist
    if node is None:
        return

    # Get the identifier of the current node
    current_id = dot_node_id(node)

    # Add the node and its label and tooltip
    lines.append(
        f'    {current_id} [label="{node_label(node)}", '
        f'tooltip="{node_tooltip(node)}"];'
    )

    # Process the left and right children
    for child, side in ((node.left, "I"), (node.right, "D")):

        # If a child does not exist, create an empty node
        if child is None:
            empty_id = f"empty_{id(node)}_{side}"

            lines.append(
                f'    {empty_id} [label="∅", shape=point];'
            )

            # Connect the current node to the empty node
            lines.append(
                f'    {current_id} -> {empty_id} [style=dashed];'
            )

        else:
            # Connect the current node with its child
            lines.append(
                f'    {current_id} -> {dot_node_id(child)};'
            )

            # Continue recursively through the child
            append_dot_edges(child, lines)


# ---------------------------------------------------------
# CONVERT THE AVL TREE INTO A GRAPHVIZ GRAPH
# ---------------------------------------------------------

def tree_to_dot(tree):

    # Graphviz visual configuration
    lines = [
        "digraph AVL {",
        '    graph [rankdir=TB, bgcolor="transparent", '
        'nodesep=0.45, ranksep=0.65];',
        '    node [shape=box, style="rounded,filled", '
        'fillcolor="#E8F1F2", color="#24545A", '
        'fontname=" sans-serif"];',
        '    edge [color="#6C7A80", arrowsize=0.7];',
    ]

    # Display an empty tree message if there is no root
    if tree.root is None:
        lines.append(
            '    empty [label="Árbol vacío", shape=box];'
        )
    else:
        # Start recursively adding the tree nodes and edges
        append_dot_edges(tree.root, lines)

    # Close the Graphviz structure
    lines.append("}")

    # Join all lines into one Graphviz string
    return "\n".join(lines)


# ---------------------------------------------------------
# CREATE TABLE ROWS FOR THE TREE NODES
# ---------------------------------------------------------

def event_rows(tree):
    rows = []

    # Recursively visit every node in the tree
    def visit(node, depth):
        if node is None:
            return

        # Get the Event stored in the node
        event = node.value

        # Get the event key values
        priority, magnitude, identifier = event.get_code()

        # Add the node information to the table
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

        # Visit the left subtree
        visit(node.left, depth + 1)

        # Visit the right subtree
        visit(node.right, depth + 1)

    # Start the traversal from the root
    visit(tree.root, 0)

    return rows


# Convert a list of events into a dictionary
# using the event identifier as the key
def format_events(events):
    return {
        f"SIS-{event.get_id():06d}": event
        for event in events
    }


# ---------------------------------------------------------
# CREATE THE SCENARIO FROM THE JSON FILE
# ---------------------------------------------------------

def create_scenario():
    # Create a new Scenario object
    scenario = Scenario()

    # Load the saved data from the JSON file
    data = cargar_json()

    # Process every earthquake stored in the file
    for sismo in data:

        # Convert the JSON data into an Event object
        event = Event(
            sismo["id"],
            sismo["magnitude"],
            sismo["depth"],
            tuple(sismo["epicenter"]),
            sismo["datetime"],
            sismo["station"],
            sismo.get("revisions", 1),
            review=sismo.get("review")
        )

        # Add the event to the scenario
        scenario.create_event(event)

    # The initial data should not count as user actions
    scenario.undo_stack.undo_actions.clear()
    scenario.undo_stack.redo_actions.clear()

    return scenario


# ---------------------------------------------------------
# STREAMLIT SESSION STATE
# ---------------------------------------------------------

# Store the minimum age required for archiving events
if "archive_age_hours" not in st.session_state:
    st.session_state.archive_age_hours = 72

# Store the selected insertion order
if "avl_insertion_order" not in st.session_state:
    st.session_state.avl_insertion_order = "Orden del archivo"

# Keep the existing AVL balance configuration
if "avl_balance_tree" not in st.session_state:
    st.session_state.avl_balance_tree = True


# Create the Scenario if it does not already exist
if "scenario" not in st.session_state:
    st.session_state.scenario = Scenario()


# Get the current Scenario
scenario = st.session_state.scenario


# ---------------------------------------------------------
# LOAD THE AVL TREE FROM THE JSON FILE
# ---------------------------------------------------------

if "arbol" not in st.session_state:

    # Load the saved earthquake data
    data = cargar_json()

    # Convert each JSON record into an Event
    for sismo in data:
        evento = Event(
            sismo["id"],
            sismo["magnitude"],
            sismo["depth"],
            tuple(sismo["epicenter"]),
            sismo["datetime"],
            sismo["station"],
            sismo.get("revisions", 1),
            review=sismo.get("review")
        )

        # Add the event to the Scenario
        scenario.create_event(evento)

    # Store the AVL tree in Streamlit session state
    st.session_state.arbol = scenario.tree

else:
    # Restore the same tree inside the Scenario
    scenario.tree = st.session_state.arbol


# Reference to the current AVL tree
tree = scenario.tree


# ---------------------------------------------------------
# SIDEBAR CONFIGURATION
# ---------------------------------------------------------

with st.sidebar:

    st.header("Ejemplo")

    # Select the order in which events are displayed
    insertion_order = st.selectbox(
        "Orden de inserción",
        (
            "Orden del archivo",
            "Clave ascendente",
            "Clave descendente"
        ),
        key="avl_insertion_order",
    )

    # Select the minimum age required for archiving
    archive_age_hours = st.number_input(
        "Antigüedad mínima T (horas)",
        min_value=1,
        step=1,
        key="archive_age_hours",
    )

    # Update the Scenario parameter if the value changed
    if tree.archive_age_hours != archive_age_hours:
        scenario.change_parameters(
            {"T": archive_age_hours}
        )

    # Search for a subtree that can be archived
    archive_candidate = scenario.archive_manager.find_candidate()

    if archive_candidate:
        st.info(
            f"Subárbol elegido automáticamente: "
            f"raíz SIS-{archive_candidate['root_id']:06d} "
            f"({archive_candidate['size']} eventos)."
        )
    else:
        st.info(
            "No hay un subárbol elegible para archivar."
        )

    # Archive the selected subtree
    if st.button(
        "Archivar subárbol",
        disabled=archive_candidate is None
    ):
        operation = scenario.archive_subtree()

        if operation:
            st.success(
                f"Se archivaron {len(operation.event_ids)} eventos: "
                f"{', '.join(f'SIS-{event_id:06d}' for event_id in sorted(operation.event_ids))}."
            )

            # Refresh the page after the operation
            st.rerun()

    # Undo the last operation
    if st.button("Deshacer última acción"):

        undone = scenario.undo()

        if undone is not None:
            st.success(
                "La última acción se deshizo correctamente."
            )
            st.rerun()
        else:
            st.info(
                "No hay acciones para deshacer."
            )

    # Redo the last operation
    if st.button("Rehacer última acción"):

        redone = scenario.redo()

        if redone is not None:
            st.success(
                "La última acción se rehizo correctamente."
            )
            st.rerun()
        else:
            st.info(
                "No hay acciones para rehacer."
            )

    # Inform the user about how example events are handled
    st.info(
        "Los eventos de ejemplo se reconstruyen en cada cambio "
        "para evitar modificar otros estados de la aplicación."
    )


# ---------------------------------------------------------
# GET EVENTS FROM THE AVL TREE
# ---------------------------------------------------------

# Get all events using an in-order traversal
events = tree.in_order() or []


# Sort events according to the selected option
if insertion_order == "Clave ascendente":

    events.sort(
        key=lambda event: event.get_code()
    )

elif insertion_order == "Clave descendente":

    events.sort(
        key=lambda event: event.get_code(),
        reverse=True
    )


# ---------------------------------------------------------
# SYNCHRONIZE AVL STATE
# ---------------------------------------------------------

# Store the current AVL information so it can be
# accessed by other parts of the application
st.session_state.avl_sync_state = {
    "active_events": deepcopy(events),
    "historic_events": deepcopy(tree.list_historic),
    "retired_ids": set(tree.retired_ids),
    "associations": deepcopy(tree.associations),
    "metrics": tree.metrics.snapshot(),
    "simulation_clock": tree.simulation_clock,
    "archive_age_hours": tree.archive_age_hours,
}


# ---------------------------------------------------------
# DISPLAY THE ACTIVE TREE
# ---------------------------------------------------------

st.subheader("Árbol activo")

# Divide the page into two columns
left_column, right_column = st.columns([2, 1])


# Left column: display the Graphviz tree
with left_column:

    st.graphviz_chart(
        tree_to_dot(tree),
        use_container_width=True
    )


# Right column: display tree statistics
with right_column:

    # Number of active events
    st.metric(
        "Eventos activos",
        len(events)
    )

    # Height of the AVL tree
    st.metric(
        "Altura",
        tree.height()
    )

    # Identifier of the root node
    st.metric(
        "Raíz",
        f"SIS-{tree.root.value.get_id():06d}"
        if tree.root
        else "-"
    )

    # Count the leaf nodes
    st.metric(
        "Hojas",
        sum(
            1
            for row in event_rows(tree)
            if row["Altura"] == 0
        )
    )


# ---------------------------------------------------------
# NODE DETAILS
# ---------------------------------------------------------

st.subheader("Detalle de nodos")

# Display all nodes and their information in a table
st.dataframe(
    event_rows(tree),
    use_container_width=True,
    hide_index=True
)

# ---------------------------------------------------------
# HISTORICAL EVENTS
# ---------------------------------------------------------

st.subheader("Histórico")

# Get all archived events
historic_events = tree.list_historic


if historic_events:

    # Prepare archived events for the table
    historic_rows = [
        {
            "Id": f"SIS-{event.get_id():06d}",
            "Priority": event.get_priority(),
            "Magnitude": event.get_magnitude(),
            "Status": "Archivado",
        }
        for event in historic_events
    ]

    # Display the historical events
    st.dataframe(
        historic_rows,
        use_container_width=True,
        hide_index=True
    )

    # Get the identifiers of historical events
    historic_ids = [
        event.get_id()
        for event in historic_events
    ]

    # Allow the user to select a historical event
    selected_historic_id = st.selectbox(
        "Evento histórico para reactivar",
        historic_ids
    )

    # Button to reactivate a historical event
    if st.button("Reactivar evento histórico"):
        operation = scenario.reactivate_event(selected_historic_id)

        if operation is not None:
            st.success(
                f"SIS-{selected_historic_id:06d} se reactivó "
                "correctamente en el AVL activo."
            )
            st.rerun()
        else:
            st.error(
                f"No se pudo reactivar SIS-{selected_historic_id:06d}. "
                "El evento puede estar activo o retirado."
            )

else:

    # Message shown when there are no archived events
    st.info("No hay eventos archivados.")


# ---------------------------------------------------------
# TREE TRAVERSALS
# ---------------------------------------------------------

st.subheader("Recorridos")

# Create four columns for the four traversals
traversal_columns = st.columns(4)

# Get the four available tree traversals
traversals = (
    ("Preorden", tree.pre_order()),
    ("Inorden", tree.in_order()),
    ("Postorden", tree.post_order()),
    ("Por niveles", tree.breadth_first()),
)


# Display each traversal in its own column
for column, (title, traversal) in zip(
    traversal_columns,
    traversals
):

    with column:

        # Convert every event into its identifier
        identifiers = [
            f"SIS-{event.get_id():06d}"
            for event in (traversal or [])
        ]

        st.write(f"*{title}*")

        # Display the traversal as a sequence
        st.code(
            " → ".join(identifiers)
            if identifiers
            else "Árbol vacío"
        )


# ---------------------------------------------------------
# ORIGINAL DESIGN
# ---------------------------------------------------------

st.caption("L")

# Main colors of the original design
color_fondo = "#6e9693"
color_texto = "#000000"
color_fondo2 = "#406e75"
color_fondo3 = "#FFFFFF"
color_boton = "#FFFFFF"
color_boton_texto = "#000000"
color_fondo_pameter = "#FFFFFF"
color_texto_pameter = "#000000"
color_fondo_ar = "#FFFFFF"
color_arriba = "#6e9693"


# ---------------------------------------------------------
# ORIGINAL STRESS MODE DESIGN
# ---------------------------------------------------------

# These colors are kept as part of the original design.
# The stress mode is not activated by this file.

stress_color_fondo = "#9c0720"
stress_color_texto = "#000000"
stress_color_fondo2 = "#610000"
stress_color_fondo3 = "#82303C"
stress_color_boton = "#734141"
stress_color_boton_texto = "#000000"
stress_color_fondo_pameter = "#352F30"
stress_color_texto_pameter = "#FFFFFF"
stress_color_fondo_ar = "#610000"
stress_color_arriba = "#9c0720"


# ---------------------------------------------------------
# BURST MODE
# ---------------------------------------------------------

# If burst mode is active, change the interface colors
# and display its corresponding image
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
    color_arriba = "#D8F3DC"

    # Display the burst mode image in the sidebar
    st.sidebar.image(
        "scr/pages/resources/amor.jpg",
        width=300
    )


# ---------------------------------------------------------
# APPLY CSS STYLES
# ---------------------------------------------------------

# Apply the selected colors to the application,
# sidebar and header
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
