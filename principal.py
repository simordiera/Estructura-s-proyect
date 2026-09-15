import streamlit as st
import pandas as pd
import plotly.express as px
import json
#NO FUN IONA NADA, GAS, NO ME TOQUEN EL CODIGO
#configuracion visual de la pag
st.set_page_config(
    page_title="SismoLab",
    page_icon= ":leaves:",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("SismoLab", text_alignment="center")


import streamlit as st
import json

if "show_options" not in st.session_state:
    st.session_state.show_options = False
if "show_form" not in st.session_state:
    st.session_state.show_form = False

#Markdown sirve pa utilizar css y html, o para mostrar texto, el unsafe permite que el streamlit permita el css
#st.markdown("""
#<style>
#div.stButton > button {
 #   width: 150px;
  #  height: 50px;
   # border-radius:20px;
    #font-size: 18px;
    # font-weight: bold;
   # transform: translateY(100px);
   # background-color:#77ACA2;
   # position:relative;
   # z-index:999;
#}
#</style>
#""", unsafe_allow_html=True)

# boton pa crear
if st.button("crear"):
    st.session_state.show_options = True

# mostrar los otros dos botoncitos
if st.session_state.show_options:
    #divede ls cosas en dos columnas, para que así los botoncitos queden al lado.
    col1, col2 = st.columns(2)

    #oprimir boton para poder cargar un archivo de tipo JSON (TENGO QUE CORREGIR LO DE QUE SE CIERRA SOLO)
    with col1:
        if st.button("Subir archivo JSON"):
            uploaded_file = st.file_uploader("Puedes subir tu archivo aquí! :)",
            type=["json"]
            )

            if uploaded_file is not None:
                data = json.load(uploaded_file)
                st.success("Archivo cargado correctamente :)")
                st.session_state.data = data
                st.session_state.show_options = False
                st.rerun()

    #segundo boton para llenar los datos manalmente(tengo que )
    with col2:
        if st.button("Llenar datos manualmente"):
            st.session_state.show_form = True

        if st.session_state.show_form:
            with st.form("my_form"):
                st.title("LLena la información del sismo :)")
                identifier = st.text_input("ingrese el identificador")
                magnitude = st.text_input("ingrese la magnitud")
                coordinates = st.text_input("coordenadas")
                date = st.text_input("fecha")
                time = st.text_input("hora")
                report_location = st.text_input("lugar del reporte")
                submitted = st.form_submit_button("Subir archivo")

                if submitted:
                    st.session_state.data = [{
                        "identificador": identifier,
                        "magnitud": magnitude,
                        "coordenadas": coordinates,
                        "fecha": date,
                        "hora": time,
                        "lugar_reporte": report_location
                    }]
                    st.session_state.show_options = False
                    st.session_state.show_form = False
                    st.rerun()
#aparece en el menu cuando se meten en la pag prin
st.sidebar.success('ya no aguanto, ya no aguanto')

#mapaaaaaa
data = pd.DataFrame({
    'lat': [5.0689, 5.0600],
    'lon': [-75.5174, -75.5000],
    'nombre': ['Centro Histórico', 'Zona Cable']
})

# 3. Creación del mapa usando la sintaxis moderna estándar
fig = px.scatter_map(
    data, 
    lat="lat", 
    lon="lon", 
    hover_name="nombre",
    zoom=11
)

# 4. Ajustes de diseño obligatorios para que cargue correctamente
fig.update_layout(
    map_style="open-street-map",
    height=600, # Forzamos una altura visible en píxeles
    margin={"r":400, "t":10, "l":400, "b":10} # Margen mínimo para evitar cortes gráficos
)
# 5. Renderizar el mapa en la pantalla
st.plotly_chart(fig, use_container_width=True)

