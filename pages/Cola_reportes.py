from datetime import date, datetime, time, timezone

import pandas as pd
import streamlit as st

from scr.models.Report import Report
from scr.models.Scenario import Scenario


st.set_page_config(
    page_title="Cola reportes",
    page_icon=":clipboard:",
    layout="wide",
)

st.title("Cola visual de reportes")
st.write(
    "En esta página se pueden preparar reportes sísmicos y dejarlos en una "
    "cola FIFO antes de procesarlos."
)
st.info(
    "Los reportes se procesan en el escenario compartido. Esta página no "
    "modifica directamente la implementación del AVL ni del BST."
)


def get_scenario():
    """Return the scenario shared by Streamlit pages."""
    if "scenario" not in st.session_state:
        st.session_state.scenario = Scenario()
    return st.session_state.scenario


def get_processed_reports():
    """Store reports that have left the queue."""
    if "processed_visual_reports" not in st.session_state:
        st.session_state.processed_visual_reports = []
    return st.session_state.processed_visual_reports


def values_have_one_decimal(value):
    """Check that a number has at most one decimal place."""
    return abs(value * 10 - round(value * 10)) < 0.000001


def make_datetime_text(selected_date, selected_time):
    """Convert date and time controls to the project's ISO format."""
    selected_datetime = datetime.combine(selected_date, selected_time)
    return selected_datetime.strftime("%Y-%m-%dT%H:%M:%S")


def get_event_rows(tree):
    """Return active events with their node height and level."""
    rows = []

    def visit(node, level):
        if node is None:
            return

        event = node.value
        rows.append(
            {
                "Evento": event,
                "Nivel": level,
                "Altura": node.height,
            }
        )
        visit(node.left, level + 1)
        visit(node.right, level + 1)

    visit(tree.root, 0)
    return rows


def event_matches(event_row, criterion, value):
    """Check whether an event matches the selected criterion."""
    event = event_row["Evento"]

    if criterion == "Magnitud":
        return abs(event.get_magnitude() - value) < 0.000001
    if criterion == "Profundidad":
        return abs(event.get_depth() - value) < 0.000001
    if criterion == "Prioridad":
        return event.get_priority() == value
    if criterion == "Altura del nodo":
        return event_row["Altura"] == value
    if criterion == "Nivel del nodo":
        return event_row["Nivel"] == value
    if criterion == "Estación":
        return value.casefold() in event.get_station().casefold()
    if criterion == "Zona":
        return event.get_zone() == value
    if criterion == "Revisiones":
        return event.get_revisions() == value
    if criterion == "Fecha":
        return event.get_datetime().date() == value

    return False


def event_to_search_row(event_row):
    """Convert an event and its node into a result row."""
    event = event_row["Evento"]
    return {
        "Identificador": f"SIS-{event.get_id():06d}",
        "Magnitud": event.get_magnitude(),
        "Profundidad (km)": event.get_depth(),
        "Prioridad": event.get_priority(),
        "Zona": event.get_zone(),
        "Altura del nodo": event_row["Altura"],
        "Nivel del nodo": event_row["Nivel"],
        "Revisiones": event.get_revisions(),
        "Estación": event.get_station(),
        "Fecha y hora": event.get_datetime().strftime("%Y-%m-%d %H:%M:%S"),
    }


scenario = get_scenario()
queue = scenario.report_queue
processed_reports = get_processed_reports()

st.header("Añadir un reporte")

with st.form("add_report_form", clear_on_submit=True):
    left_column, middle_column, right_column = st.columns(3)

    with left_column:
        identifier = st.number_input(
            "Identificador del evento",
            min_value=1,
            max_value=999999,
            value=1,
            step=1,
        )
        magnitude = st.number_input(
            "Magnitud",
            min_value=-2.0,
            max_value=10.0,
            value=2.0,
            step=0.1,
            format="%.1f",
        )
        depth = st.number_input(
            "Profundidad del hipocentro (km)",
            min_value=0.0,
            max_value=700.0,
            value=10.0,
            step=0.1,
            format="%.1f",
        )

    with middle_column:
        epicenter_x = st.number_input(
            "Epicentro X (km)",
            min_value=0.0,
            max_value=1000.0,
            value=0.0,
            step=0.1,
            format="%.1f",
        )
        epicenter_y = st.number_input(
            "Epicentro Y (km)",
            min_value=0.0,
            max_value=1000.0,
            value=0.0,
            step=0.1,
            format="%.1f",
        )
        revision = st.number_input(
            "Número de revisión",
            min_value=1,
            value=1,
            step=1,
        )

    with right_column:
        station = st.text_input("Estación emisora", placeholder="Ejemplo: STA-01")
        occurrence_date = st.date_input(
            "Fecha de ocurrencia",
            value=date.today(),
        )
        occurrence_time = st.time_input(
            "Hora de ocurrencia UTC",
            value=time(12, 0),
        )

    add_report = st.form_submit_button("Añadir reporte a la cola")

if add_report:
    identifier = int(identifier)
    revision = int(revision)
    station = station.strip()
    occurrence_datetime = make_datetime_text(occurrence_date, occurrence_time)

    report = Report(
        identifier=identifier,
        magnitude=float(magnitude),
        depth=float(depth),
        epicenter=(float(epicenter_x), float(epicenter_y)),
        occurrence_datetime=occurrence_datetime,
        revision=revision,
        station=station,
    )

    errors = []

    if not station:
        errors.append("La estación emisora es obligatoria.")

    if not values_have_one_decimal(float(magnitude)):
        errors.append("La magnitud debe tener como máximo un decimal.")

    if not values_have_one_decimal(float(depth)):
        errors.append("La profundidad debe tener como máximo un decimal.")

    if not values_have_one_decimal(float(epicenter_x)) or not values_have_one_decimal(float(epicenter_y)):
        errors.append("Las coordenadas deben tener como máximo un decimal.")

    current_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    report_datetime = datetime.fromisoformat(occurrence_datetime)
    if report_datetime > current_utc:
        errors.append("La fecha de ocurrencia no puede estar en el futuro UTC.")

    if not report.is_valid():
        errors.append("Los datos del reporte no cumplen los rangos permitidos.")

    if errors:
        for error in errors:
            st.error(error)
    else:
        scenario.add_report(report)
        st.success(
            f"El reporte SIS-{identifier:06d} se agregó correctamente "
            f"al final de la cola."
        )


st.divider()
st.header("Buscar sismos por característica")
st.caption(
    "La búsqueda no usa el identificador y solo consulta los sismos activos "
    "del AVL."
)

search_rows = get_event_rows(scenario.tree)
criteria = [
    "Magnitud",
    "Profundidad",
    "Prioridad",
    "Altura del nodo",
    "Nivel del nodo",
    "Estación",
    "Zona",
    "Revisiones",
    "Fecha",
]

with st.form("search_event_form"):
    search_criterion = st.selectbox("Característica", criteria)

    if search_criterion == "Magnitud":
        search_value = st.number_input(
            "Magnitud exacta",
            min_value=-2.0,
            max_value=10.0,
            value=2.0,
            step=0.1,
            format="%.1f",
        )
    elif search_criterion == "Profundidad":
        search_value = st.number_input(
            "Profundidad exacta (km)",
            min_value=0.0,
            max_value=700.0,
            value=10.0,
            step=0.1,
            format="%.1f",
        )
    elif search_criterion == "Prioridad":
        search_value = st.selectbox("Prioridad", [1, 2, 3])
    elif search_criterion == "Altura del nodo":
        search_value = st.number_input(
            "Altura exacta",
            min_value=1,
            max_value=1000,
            value=1,
            step=1,
        )
    elif search_criterion == "Nivel del nodo":
        search_value = st.number_input(
            "Nivel exacto",
            min_value=0,
            max_value=1000,
            value=0,
            step=1,
        )
    elif search_criterion == "Estación":
        search_value = st.text_input("Texto de la estación")
    elif search_criterion == "Zona":
        search_value = st.selectbox("Zona", ["poblada", "no poblada"])
    elif search_criterion == "Revisiones":
        search_value = st.number_input(
            "Número exacto de revisiones",
            min_value=1,
            value=1,
            step=1,
        )
    else:
        search_value = st.date_input("Fecha exacta")

    search_events = st.form_submit_button("Buscar sismos")

if search_events:
    matching_rows = [
        event_row
        for event_row in search_rows
        if event_matches(event_row, search_criterion, search_value)
    ]

    if matching_rows:
        st.success(f"Se encontraron {len(matching_rows)} sismo(s).")
        st.dataframe(
            [event_to_search_row(row) for row in matching_rows],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No se encontraron sismos con esa característica.")


st.divider()
st.header("Reportes pendientes")

pending_reports = queue.get_all()

if not pending_reports:
    st.info("No hay reportes pendientes en la cola.")
else:
    first_report = queue.peek()
    st.warning(
        f"Siguiente reporte FIFO: SIS-{first_report.identifier:06d} "
        f"(estación {first_report.station}, revisión {first_report.revision})."
    )

    if st.button("Procesar siguiente reporte"):
        operation = scenario.process_next_report()
        if operation is not None:
            processed_report = operation.report
            processed_reports.append(processed_report)
            st.success(
                operation.result["message"]
            )
            st.rerun()

    pending_rows = []
    for position, report in enumerate(pending_reports, start=1):
        row = report.to_dict()
        row["Posición FIFO"] = position
        pending_rows.append(row)

    st.dataframe(
        pd.DataFrame(pending_rows),
        use_container_width=True,
        hide_index=True,
    )


st.divider()
st.header("Reportes procesados en esta sesión")

if processed_reports:
    processed_rows = []
    for report in processed_reports:
        processed_rows.append(report.to_dict())

    st.dataframe(
        pd.DataFrame(processed_rows),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("Todavía no se ha procesado ningún reporte.")


with st.sidebar:
    st.header("Resumen de la cola")
    st.metric("Pendientes", len(queue.get_all()))
    st.metric("Procesados", len(processed_reports))
    st.caption(
        "La cola mantiene el orden de llegada. La magnitud no cambia la "
        "posición FIFO del reporte."
    )

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