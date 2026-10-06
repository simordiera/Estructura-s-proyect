import streamlit as st
import pandas as pd
# History view.
st.title("historial de los sismos creados", text_alignment="center")

if "data" in st.session_state:

    data = st.session_state.data

    df = pd.DataFrame(data)

    event = st.dataframe(
        df,
        key="data",
        on_select="rerun",
        selection_mode=["multi-row", "multi-column", "multi-cell"],
    )

    st.write(event.selection)
