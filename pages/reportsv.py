from datetime import date, datetime, time, timezone

import pandas as pd
import streamlit as st

from scr.models.Report import Report
from scr.models.Scenario import Scenario


st.set_page_config(
    page_title="Cola de reportes",
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
    """Obtiene el escenario compartido por las páginas de Streamlit."""
    if "scenario" not in st.session_state:
        st.session_state.scenario = Scenario()
    return st.session_state.scenario


def get_processed_reports():
    """Guarda aparte los reportes que ya salieron de la cola."""
    if "processed_visual_reports" not in st.session_state:
        st.session_state.processed_visual_reports = []
    return st.session_state.processed_visual_reports


def values_have_one_decimal(value):
    """Comprueba que un número no tenga más de un decimal."""
    return abs(value * 10 - round(value * 10)) < 0.000001


def make_datetime_text(selected_date, selected_time):
    """Convierte los controles de fecha y hora al formato ISO del proyecto."""
    selected_datetime = datetime.combine(selected_date, selected_time)
    return selected_datetime.strftime("%Y-%m-%dT%H:%M:%S")


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