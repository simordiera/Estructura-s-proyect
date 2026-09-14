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

if "mostrar_opciones" not in st.session_state:
    st.session_state.mostrar_opciones = False
if "mostrar_formulario" not in st.session_state:
    st.session_state.mostrar_formulario = False

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
    st.session_state.mostrar_opciones = True

# mostrar los otros dos botoncitos
if st.session_state.mostrar_opciones:
    #divede ls cosas en dos columnas, para que así los botoncitos queden al lado.
    col1, col2 = st.columns(2)

    #oprimir boton para poder cargar un archivo de tipo JSON (TENGO QUE CORREGIR LO DE QUE SE CIERRA SOLO)
    with col1:
        if st.button("Subir archivo JSON"):
            archivo = st.file_uploader("Puedes subir tu archivo aquí! :)",
            type=["json"]
            )

            if archivo is not None:
                datos= json.load(archivo)
                st.success("Archivo cargado correctamente :)")
                st.session_state.datos = datos
                st.session_state.mostrar_opciones = False
                st.rerun()

    #segundo boton para llenar los datos manalmente(tengo que )
    with col2:
        if st.button("Llenar datos manualmente"):
            st.session_state.mostrar_formulario = True

        if st.session_state.mostrar_formulario:
            with st.form("my_form"):
                st.title("LLena la información del sismo :)")
                identificador=st.text_input("ingrese el identificador")
                magnitud=st.text_input("ingrese la magnitud")
                coordenadas=st.text_input("coordenadas")
                fecha=st.text_input("fecha")
                hora=st.text_input("hora")
                lugar_reporte=st.text_input("lugar del reporte")
                submitted = st.form_submit_button("Subir archivo")

                if submitted:
                    st.session_state.datos = [{
                        "identificador": identificador,
                        "magnitud": magnitud,
                        "coordenadas": coordenadas,
                        "fecha": fecha,
                        "hora": hora,
                        "lugar_reporte": lugar_reporte
                    }]
                    st.session_state.mostrar_opciones = False
                    st.session_state.mostrar_formulario = False
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

