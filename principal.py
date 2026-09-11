import streamlit as st
import pandas as pd
import plotly.express as px

#configuracion visual de la pag
st.set_page_config(
    page_title="SismoLab",
    page_icon= ":leaves:",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("SismoLab", text_alignment="center")
st.sidebar.success('ya no aguanto, ya no aguanto')

st.file_uploader("Aqui puedes subir tu archivo! :)")

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

