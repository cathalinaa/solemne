import pandas as pd
import requests
import streamlit as st
import io

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

# Llamar la función para obtener los datos
data = obtener_datos_paises()

# Si hay datos, convertir a DataFrame y mostrar
if data is not None:
    df = convertir_a_dataframe(data)

    # Mostrar el DataFrame
    st.title("Interacción con los datos:")
    st.write("Mostrar datos originales:")
    st.dataframe(df)

    st.header("Selecciona una columna del dataframe utilizando un menú desplegable")
    columnas_seleccionadas = st.multiselect('Selecciona las columnas a visualizar', df.columns.tolist(), default=df.columns.tolist())
    df_seleccionado = df[columnas_seleccionadas]

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

    columna_filtro = st.selectbox("Selecciona una columna para filtrar:", df.select_dtypes(include=['number']).columns)
    if columna_filtro:
        min_val, max_val = st.slider(
            f"Selecciona el rango para {columna_filtro}:",
            float(df[columna_filtro].min()),
            float(df[columna_filtro].max()),
            (float(df[columna_filtro].min()), float(df[columna_filtro].max()))
        )
        df_filtrado = df[(df[columna_filtro] >= min_val) & (df[columna_filtro] <= max_val)]
        st.write("**Datos Filtrados:**")
        st.write(df_filtrado)

        # Botón para descargar los datos filtrados
        st.subheader("Exportar Datos Filtrados")
        formato = st.radio("Elige el formato para descargar:", ('CSV', 'Excel'))

        @st.cache_data
        def convertir_a_csv(dataframe):
            return dataframe.to_csv(index=False)

        @st.cache_data
        def convertir_a_excel(dataframe):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                dataframe.to_excel(writer, index=False, sheet_name='Datos')
            output.seek(0)
            return output.getvalue()
            
            if st.button("Descargar"):
                if formato == 'CSV':
                    csv = convertir_a_csv(df_filtrado)
                    st.download_button("Descargar CSV", csv, "datos_filtrados.csv", "text/csv")
                elif formato == 'Excel':
                    excel = convertir_a_excel(df_filtrado)
                    st.download_button("Descargar Excel", excel, "datos_filtrados.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
