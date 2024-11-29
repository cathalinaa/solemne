# -*- coding: utf-8 -*-
"""Aplicación de Streamlit para interactuar con datos de países"""

import pandas as pd
import streamlit as st
import io

def obtener_datos_api(url):
    """Función que realiza la petición a la API y devuelve un DataFrame."""
    return pd.read_excel(url)

# Llamar la función para obtener los datos
api_url = "https://github.com/cathalinaa/solemne/raw/main/datos_paises_procesados.xlsx"  # Asegúrate de usar la URL correcta para el archivo crudo
df = obtener_datos_api(api_url)

# Si hay datos, mostrar el DataFrame
if df is not None:
    st.write(df.head())

    # Selección de columnas relevantes
    df['Nombre'] = df['name'].apply(lambda x: x.get('common') if isinstance(x, dict) else None)
    df['Región'] = df['region']
    df['Población'] = df['population']
    df['Área (km²)'] = df['area']
    df['Fronteras'] = df['borders'].apply(lambda x: len(x) if isinstance(x, list) else 0)
    df['Idiomas Oficiales'] = df['languages'].apply(lambda x: len(x) if isinstance(x, dict) else 0)
    df['Zonas Horarias'] = df['timezones'].apply(lambda x: len(x) if isinstance(x, list) else 0)

    # Filtrar columnas seleccionadas
    columnas = ['Nombre', 'Región', 'Población', 'Área (km²)', 'Fronteras', 'Idiomas Oficiales', 'Zonas Horarias']
    df_cleaned = df[columnas]

    # Mostrar DataFrame con las columnas seleccionadas
    st.title("Interacción con los datos:")
    st.write("Mostrar datos originales:")
    st.dataframe(df_cleaned)

    st.header("Selecciona una columna del dataframe utilizando un menú desplegable")
    columnas_seleccionadas = st.multiselect('Selecciona las columnas a visualizar', df_cleaned.columns.tolist(), default=df_cleaned.columns.tolist())
    df_seleccionado = df_cleaned[columnas_seleccionadas]

    # Mostrar el DataFrame con las columnas seleccionadas
    st.write('Columnas Seleccionadas:')
    st.write(df_seleccionado)
    st.write("Estadísticas de las columnas seleccionadas:")
    st.write("Media:", df_seleccionado.mean(numeric_only=True))
    st.write("Mediana:", df_seleccionado.median(numeric_only=True))
    st.write("Desviación estándar:", df_seleccionado.std(numeric_only=True))

    columna_ordenar = st.selectbox('Selecciona una columna para ordenar', df_seleccionado.columns)
    # Control para seleccionar el orden (ascendente o descendente)
    orden = st.radio('Selecciona el orden:', ('Ascendente', 'Descendente'))
    # Ordenar el DataFrame según la columna seleccionada y el orden elegido
    df_ordenado = df_seleccionado.sort_values(by=columna_ordenar, ascending=(orden == 'Ascendente'))
    
    # Mostrar el DataFrame ordenado
    st.write('DataFrame Ordenado:')
    st.write(df_ordenado)

    columna_filtro = st.selectbox("Selecciona una columna para filtrar:", df_cleaned.select_dtypes(include=['number']).columns)
    if columna_filtro:
        min_val, max_val = st.slider(
            f"Selecciona el rango para {columna_filtro}:",
            float(df_cleaned[columna_filtro].min()),
            float(df_cleaned[columna_filtro].max()),
            (float(df_cleaned[columna_filtro].min()), float(df_cleaned[columna_filtro].max()))
        )
        df_filtrado = df_cleaned[(df_cleaned[columna_filtro] >= min_val) & (df_cleaned[columna_filtro] <= max_val)]
        st.write("**Datos Filtrados:**")
        st.write(df_filtrado)

        # Botón para descargar los datos filtrados
        st.subheader("Exportar Datos Filtrados")
        formato = st.radio("Elige el formato para descargar:", ('CSV', 'Excel'))

        @st.cache_data
        def convertir_a_csv(df):
            return df.to_csv(index=False).encode('utf-8')

        @st.cache_data
        def convertir_a_excel(df):
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
