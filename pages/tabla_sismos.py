import streamlit as st
import pandas as pd
#ESTE TAMPOCO M LO TOQUEN
st.title("tabla de los sismos creados", text_alignment="center")

if "data" not in st.session_state:
    st.session_state.data = []

datos = st.session_state.data

df = pd.DataFrame(datos)

event = st.dataframe(
    df,
    key="dataframe",
)
