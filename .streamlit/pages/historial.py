import streamlit as st
import pandas as pd
#ESTE TAMPOCO M LO TOQUEN
st.title("historial de los sismos creados", text_alignment="center")

if "datos" in st.session_state:

    datos = st.session_state.datos

    df = pd.DataFrame(datos)

    event = st.dataframe(
        df,
        key="data",
        on_select="rerun",
        selection_mode=["multi-row", "multi-column", "multi-cell"],
    )

    st.write(event.selection)
