import pandas as pd
import requests
import streamlit as st

def obtener_datos_paises():
    url = 'https://raw.githubusercontent.com/jxnscv/Programacion/main/all.json' 
    respuesta = requests.get(url)
    if respuesta.status_code == 200:
        return respuesta.json()  # Retornar el contenido JSON
    else:
        st.error(f'Error: {respuesta.status_code}')
        return None

def convertir_a_dataframe(paises):
    datos = []
    for pais in paises:
        datos.append({
            'Nombre Común': pais.get('name', {}).get('common', 'No disponible'),
            'Región Geográfica': pais.get('region', 'No disponible'),
            'Población Total': pais.get('population', 0),
            'Área en km²': pais.get('area', 0),
            'Número de Fronteras': len(pais.get('borders', [])),
            'Número de Idiomas Oficiales': len(pais.get('languages', {})),
            'Número de Zonas Horarias': len(pais.get('timezones', [])),
            'Latitud': pais.get('latlng', [None, None])[0],
            'Longitud': pais.get('latlng', [None, None])[1]
        })
    return pd.DataFrame(datos)

df = obtener_datos_paises()

# Si hay datos, mostrar el DataFrame
if df is not None:
    # Convertir la respuesta JSON a un DataFrame
    df = pd.json_normalize(df)

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
    
    # Mostrar estadísticas
    st.write("Estadísticas de las columnas seleccionadas:")
    st.write("Media:", df_seleccionado.mean(numeric_only=True))
    st.write("Mediana:", df_seleccionado.median(numeric_only=True))
    st.write("Desviación estándar:", df_seleccionado.std(numeric_only=True))

    columna_ordenar = st.selectbox('Selecciona una columna para ordenar', df_seleccionado.columns)
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
        def convertir_a_excel(df):
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Datos')
            buffer.seek(0)
            return buffer.getvalue()

        if st.button("Descargar"):
            if formato == 'CSV':
                csv = convertir_a_csv(df_filtrado)
                st.download_button(
                    label="Descargar CSV",
                    data=csv,
                    file_name='datos_filtrados.csv',
                    mime='text/csv'
                )
            elif formato == 'Excel':
                excel = convertir_a_excel(df_filtrado)
                st.download_button(
                    label="Descargar Excel",
                    data=excel,
                    file_name='datos_filtrados.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
