import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import numpy as np

## Configuración inicial de la página
st.set_page_config(
    page_title="Dashboard por Equipo CSC",
    page_icon=":bar_chart:",
    layout="wide"
)

st.markdown(
    """
    <div style="
        background-color: #E0E0E0;
        padding: 1px 10px;
        border-radius: 5px;
        display: flex;
        align-items: center;">
        <img src="https://www.nibol.com.bo/wp-content/uploads/2022/06/logo-nibol-negro-ok1.png" width="250" style="margin-right: 100px;"/>
        <h1 style="color: #000000; margin: 0; font-size: 42px;">
            Reporte Seguimiento CSC
        </h1>
    </div>
    <hr style="border: none; border-top: 3px solid #000000; margin: 5px 0;">
    """,
    unsafe_allow_html=True
)
st.markdown("")
st.markdown("")
# Cargar los datos con caching para evitar recargar el archivo si no es necesario
@st.cache_data
def load_data(file):
    data = pd.read_csv(file)
    return data

# Configuración del sidebar
with st.sidebar:
    st.header("Configuración")
    uploaded_file = st.file_uploader("Elija un archivo")

# Verificar si se ha cargado un archivo
if uploaded_file is None:
    st.info("Se requiere cargar un archivo", icon="ℹ️")
    st.stop()

# Cargar y limpiar los datos
df_Original = load_data(uploaded_file)
df = df_Original.drop_duplicates()
df['Serie']=df['Serie'].replace('En reposo', 'Ralentí')

# Obtener valores clave para mostrar en la interfaz
FechaInicio = df['Fecha de inicio'].max()
FechaTerminación = df['Fecha de terminación'].max()
Chasis = df['Número de serie de la máquina'].max()
st.markdown("")
st.markdown(
    """
    <div style="
        background-color: #E0E0E0;
        padding: 1px 10px;
        border-radius: 5px;
        display: flex;
        ">
        <h2 style="
            color: #000000;
            margin: 0;
            font-size: 22px;
            font-weight: bold;
            text-align: center;
            ">
            Datos Generales
        </h2>
    </div>
    """,
    unsafe_allow_html=True
)

# Crear un diccionario con los nombres de los meses abreviados en español
meses_abreviados = {
    1: "ene", 2: "feb", 3: "mar", 4: "abr", 5: "may", 6: "jun",
    7: "jul", 8: "ago", 9: "sep", 10: "oct", 11: "nov", 12: "dic"
}

# Obtener la fecha actual
hoy = datetime.now()
dia = hoy.day
mes = meses_abreviados[hoy.month]  # Obtener la abreviatura del mes
año = hoy.year

# Crear la fecha en el formato deseado
fecha_actual = f"{dia} {mes} {año}"

# Mostrar gráficos en la misma fila
col1, col2 = st.columns([1, 1])

with col1:
    st.text_input("", placeholder="Escriba el nombre del cliente aquí")
    st.markdown(f"**Fecha del Reporte:** {fecha_actual}")
    st.markdown(f"**PIN:** {Chasis}")
    st.markdown(f"**Periodo de Análisis:** Del {FechaInicio} al {FechaTerminación}")

with col2:
    from PIL import Image
    with st.sidebar:
        st.header("Carga de imágen")
        uploaded_image = st.file_uploader("Selecciona una imagen", type=["png", "jpg", "jpeg"])
    if uploaded_image is not None:
    # Abrir y mostrar la imagen cargada
        image = Image.open(uploaded_image)
        st.image(image, use_column_width=True)

# Expander para mostrar los datos cargados
with st.expander("Vista de datos Cargados"):
    st.dataframe(df)

st.markdown(
    """
    <div style="
        background-color: #E0E0E0;
        padding: 1px 10px;
        border-radius: 5px;
        display: flex;
        ">
        <h2 style="
            color: #000000;
            margin: 0;
            font-size: 22px;
            font-weight: bold;
            text-align: left;
            ">
            Información sobre el consumo de combustible
        </h2>
    </div>
    """,
    unsafe_allow_html=True
)

# Función para graficar barras
def graficar_barras(df, categoria_seleccionada):
    df_filtrado = df[df['Categoría'] == categoria_seleccionada].sort_values(['Valor'],ascending=False)
    valor_unidades = df_filtrado['Unidades de medida'].max()

    fig = px.bar(
        df_filtrado, 
        x='Serie', 
        y='Valor', 
        title=f'Categoría: {categoria_seleccionada} - {valor_unidades}',
        labels={'Valor':f'Valor ({valor_unidades})', 'Serie':''},
        template='plotly_white',
        color_discrete_sequence=['#367C2B', '#FFCC00', '#A2B5A1', '#556B2F', '#8B4513']
    )

    fig.update_layout(
        title_font_size=20,
        xaxis_title_font_size=16,
        yaxis_title_font_size=16,
        margin=dict(l=50, r=50, t=50, b=50),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, zeroline=False),
        font=dict(family="Arial", size=12),
    )
    fig.update_traces(text=df_filtrado['Valor'], textposition='outside')

    return fig

import plotly.express as px

def graficar_pie(df, categoria_seleccionada):
    df_filtrado = df[df['Categoría'] == categoria_seleccionada]
    valor_unidades = df_filtrado['Unidades de medida'].max()
    fig = px.pie(
        df_filtrado,
        names='Serie',
        values='Valor',
        title=f'Categoría: {categoria_seleccionada} - {valor_unidades}',
        template='plotly_white',
        color_discrete_sequence=['#367C2B', '#FFCC00', '#A2B5A1', '#556B2F', '#8B4513']
    )
    fig.update_traces(
        textinfo='label+percent+value',  # Muestra el nombre, el porcentaje y el valor
        texttemplate='%{label}: %{value} (%{percent})',  # Personaliza el formato de la etiqueta
        textposition='inside',  # Coloca el texto dentro de cada porción
    )
    fig.update_layout(
        title_font_size=20,
        margin=dict(l=50, r=50, t=50, b=50),
        font=dict(family="Arial", size=12),
    )
    return fig


# Asegurar que la columna 'Valor' sea numérica
df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')

# Filtrar la columna 'Categoría'
categorias = df['Categoría'].unique()

if (df['Categoría'] == "Combustible consumido en período").any():
    Combustible_consumido=df.loc[df['Categoría']=="Combustible consumido en período"]['Valor'].max()
    st.markdown("")
    st.markdown(f"<div style='font-size: 22px;'>El total de consumible consumido en el periodo es de {Combustible_consumido} l </div>", unsafe_allow_html=True)
    st.markdown("")
elif(df['Categoría'] == "Combustible consumido").any():
    Combustible_consumido=df.loc[df['Categoría']=="Combustible consumido"]['Valor'].max()
    Combustible_promedio_consumido=df.loc[df['Categoría']=="Consumo promedio combustible"]['Valor'].max()
    st.markdown("")
    st.markdown(f"<div style='font-size: 22px;'>El total de consumible consumido en el periodo es de {Combustible_consumido} l equivalente a {Combustible_promedio_consumido} l/h </div>", unsafe_allow_html=True)
    st.markdown("")
else:   
    st.write("")
# Mostrar gráficos en la misma fila
col1, col2 = st.columns([1, 1])

with col1:
    # Determinar la categoría seleccionada
    if (df['Categoría'] == "Utilización del combustible del motor").any():
        categoria_seleccionada = "Utilización del combustible del motor"
    else:
        categoria_seleccionada = "Combustible consumido" 

    # Generar gráfico con la categoría seleccionada
    fig1 = graficar_barras(df, categoria_seleccionada)
    st.plotly_chart(fig1)

with col2:
    # Determinar la categoría seleccionada
    if (df['Categoría'] == "Índice de utilización de combustible del motor").any():
        categoria_seleccionada2 = "Índice de utilización de combustible del motor"
    else:
        categoria_seleccionada2 = "Consumo promedio combustible"
    fig2 = graficar_barras(df, categoria_seleccionada2)
    st.plotly_chart(fig2)

st.markdown(
    """
    <div style="
        background-color: #E0E0E0;
        padding: 1px 10px;
        border-radius: 5px;
        display: flex;
        ">
        <h2 style="
            color: #000000;
            margin: 0;
            font-size: 22px;
            font-weight: bold;
            text-align: left;
            ">
            Información sobre el funcionamiento del motor
        </h2>
    </div>
    """,
    unsafe_allow_html=True
)

# Corregir ralenti y filtros reporte

df_Motor=df
df_Motor=df_Motor.loc[df_Motor['Serie'].isin(['Ralentí', 'Cosecha', 'Trabajando','En reposo','Carga baja','Carga alta','Carga mediana','Llave On','Maniobra','850','1050','1350','1650','1950'])]

# Mostrar gráficos en la misma fila
col1, col2 = st.columns([1, 1])



with col1:
    # Determinar la categoría seleccionada
    if (df['Categoría'] == "Factor de carga prom del motor").any():
        categoria_seleccionada_Fig2_1 = "Factor de carga prom del motor"
    else:
        categoria_seleccionada_Fig2_1 = "Utilización del motor" 
    fig2_1 = graficar_barras(df_Motor,categoria_seleccionada_Fig2_1)
    st.plotly_chart(fig2_1)

with col2:
    # Determinar la categoría seleccionada
    if (df['Categoría'] == "Régimen de motor promedio").any():
        categoria_seleccionada_Fig2_2 = "Régimen de motor promedio"
    else:
        categoria_seleccionada_Fig2_2 = "Régimen del motor con 80-90% de carga"
    fig2_2 = graficar_barras(df_Motor,categoria_seleccionada_Fig2_2)
    st.plotly_chart(fig2_2)

st.markdown(
    """
    <div style="
        background-color: #E0E0E0;
        padding: 1px 10px;
        border-radius: 5px;
        display: flex;
        ">
        <h2 style="
            color: #000000;
            margin: 0;
            font-size: 22px;
            font-weight: bold;
            text-align: left;
            ">
           Información temperaturas de funcionamiento
        </h2>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("")
MaxTempHistoAceiteHidrau=df.loc[df['Categoría']=="Histograma de temperatura de aceite hidráulico"]['Valor'].max()
PromTempHistoAceiteHidrau=df.loc[df['Categoría']=="Histograma de temperatura de aceite hidráulico"]['Valor'].mean()
TiempoRalenti=df.loc[df['Categoría']=="Tiempo a ralentí"]['Valor'].max()
TiempoCosecha=df.loc[df['Categoría']=="Tiempo de cosecha"]['Valor'].max()
TiempoManiobra=df.loc[df['Categoría']=="Tiempo de maniobra"]['Valor'].max()
TiempoTransporte=df.loc[df['Categoría']=="Tiempo de transporte"]['Valor'].max()
Temperaturaref_prom=df.loc[df['Categoría']=="Temp de refrigerante promedio"]['Valor'].max()
Temperaturamax_hidr=df.loc[df['Categoría']=="Temp máx de aceite hidráulico"]['Valor'].max()
Temperaturamax_ref=df.loc[df['Categoría']=="Temp máx refrigerante"]['Valor'].max()
TemperaturaProm_hidr=df.loc[df['Categoría']=="Temp promedio de aceite hidráulico"]['Valor'].max()

col1, col2 = st.columns([1,1])
st.markdown("")
with col1:
    st.markdown(
        f"""
        <div style="
            background-color:rgb(248, 248, 248);
            border: 2px solid #ddd;
            border-radius: 2px;
            padding: 10px 15px;
            font-family: Arial, sans-serif;
        ">
            <b style="font-size: 16px;">Temperatura Refrigerante</b>
            <div style="margin-top: 8px; font-size: 14px;">
                Promedio: {Temperaturaref_prom} °C<br>
                Máximo: {Temperaturamax_ref} °C
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f"""
        <div style="
            background-color:rgb(248, 248, 248);
            border: 2px solid #ddd;
            border-radius: 2px;
            padding: 10px 15px;
            font-family: Arial, sans-serif;
        ">
            <b style="font-size: 16px;">Temperatura Aceite Hidráulico</b>
            <div style="margin-top: 8px; font-size: 14px;">
                Maxima: {MaxTempHistoAceiteHidrau if not np.isnan(MaxTempHistoAceiteHidrau) else Temperaturamax_hidr} °C<br>
                Promedio: {round(PromTempHistoAceiteHidrau if not np.isnan(PromTempHistoAceiteHidrau) else TemperaturaProm_hidr, 2)} °C
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("")





if(df['Categoría'] == "AutoTrac™").any():
    st.markdown(
        """
        <div style="
            background-color: #E0E0E0;
            padding: 1px 10px;
            border-radius: 5px;
            display: flex;
            ">
            <h2 style="
                color: #000000;
                margin: 0;
                font-size: 22px;
                font-weight: bold;
                text-align: left;
                ">
            Información sobre la Utilización de tecnología
            </h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("")

    col1, col2,col3 = st.columns([1,1,1])

    with col1:
            fig4_1 = graficar_pie(df,"Harvest Monitor System")
            st.plotly_chart(fig4_1)
    with col2:
            fig4_2 = graficar_pie(df, "AutoTrac™")
            st.plotly_chart(fig4_2)
    with col3:
            fig4_3 = graficar_pie(df, "SmartClean System Hours")
            st.plotly_chart(fig4_3)
else:
    st.markdown("")






if(df['Categoría'] == "Presión de cuchilla inferior máxima").any():
    st.markdown(
        """
        <div style="
            background-color: #E0E0E0;
            padding: 1px 10px;
            border-radius: 5px;
            display: flex;
            ">
            <h2 style="
                color: #000000;
                margin: 0;
                font-size: 22px;
                font-weight: bold;
                text-align: left;
                ">
            Información sobre el extractor primario y presión de cuchillas
            </h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    Presiondecuchillainferiormaxima=df.loc[df['Categoría']=="Presión de cuchilla inferior máxima"]['Valor'].max()
    Presióndepicadormaxima=df.loc[df['Categoría']=="Presión de picador máxima"]['Valor'].max()
    PrimaryExtractorFanSpeed=df.loc[df['Categoría']=="Primary Extractor Fan Speed"]['Valor'].max()
    PrimaryExtractorLossTarget=df.loc[df['Categoría']=="Primary Extractor Loss Target"]['Valor'].max()
    st.markdown("")

    col1, col2 = st.columns([1,1])
    st.markdown("")
    with col1:
        st.markdown(
            f"""
            <div style="
                background-color:rgb(248, 248, 248);
                border: 2px solid #ddd;
                border-radius: 2px;
                padding: 10px 15px;
                font-family: Arial, sans-serif;
            ">
                <b style="font-size: 16px;">Presión de Cuchillas</b>
                <div style="margin-top: 8px; font-size: 14px;">
                    Presión maxima de cuchilla inferior: {Presiondecuchillainferiormaxima} Kpa<br>
                    Presión máxima Picador: {Presióndepicadormaxima} Kpa
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
            st.markdown(
            f"""
            <div style="
                background-color:rgb(248, 248, 248);
                border: 2px solid #ddd;
                border-radius: 2px;
                padding: 10px 15px;
                font-family: Arial, sans-serif;
            ">
                <b style="font-size: 16px;">Extractor Primario</b>
                <div style="margin-top: 8px; font-size: 14px;">
                    Presión maxima de cuchilla inferior: {PrimaryExtractorFanSpeed} RPM<br>
                    Presión máxima Picador: {PrimaryExtractorLossTarget} Ton/hec
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.markdown("")








if(df['Categoría'] == "Velocidad de avance prom").any():
    st.markdown(
        """
        <div style="
            background-color: #E0E0E0;
            padding: 1px 10px;
            border-radius: 5px;
            display: flex;
            ">
            <h2 style="
                color: #000000;
                margin: 0;
                font-size: 22px;
                font-weight: bold;
                text-align: left;
                ">
            Información sobre la Utilización de la máquina y velocidad
            </h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("")

    col1, col2 = st.columns([1,1])

    with col1:
            fig6_1 = graficar_barras(df,"Utilización de la máquina")
            st.plotly_chart(fig6_1)
    with col2:
            fig6_2 = graficar_barras(df, "Velocidad de avance prom")
            st.plotly_chart(fig6_2)
else:
    st.markdown("")










if(df['Categoría'] == "Precisión del receptor StarFire™ de la máquina").any():
    st.markdown(
        """
        <div style="
            background-color: #E0E0E0;
            padding: 1px 10px;
            border-radius: 5px;
            display: flex;
            ">
            <h2 style="
                color: #000000;
                margin: 0;
                font-size: 22px;
                font-weight: bold;
                text-align: left;
                ">
            Precision señal piloto automatico
            </h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("")

    fig6_1 = graficar_barras(df,"Precisión del receptor StarFire™ de la máquina")
    st.plotly_chart(fig6_1)
else:
    st.markdown("")
