import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="BizIntelligence Aroma & Grano", layout="wide")
st.title(" BI Dashboard: Aroma & Grano")

# --- CARGA PROFESIONAL ---
@st.cache_data
def cargar_inventario():
    # Usamos low_memory=False para archivos grandes (en este caso es pequeño pero es buena práctica)
    return pd.read_csv("ventas_pro.csv")

df = cargar_inventario()

# --- SONDEO INICIAL (Teoría en acción) ---
st.header("1. Sondeo de Categorías")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Productos Únicos", df['producto'].nunique())
    
with col2:
    st.write("Tipos de productos encontrados:")
    st.write(df['tipo'].unique())

with col3:
    st.write("Frecuencia de ventas por producto:")
    st.write(df['producto'].value_counts())
st.text_area(" Explora el Dataset, para entender con que vamos a tratar , en este paso se hace un analisis inicial  de los datos , primero se calcula cuantos productos diferentes existen utilizando el nunique, luego se muestran los tipos de productos que hay en la columna" \
" y despues utiliza value_counts () para ver cuantas veces aparece cada producto , es como identificar cuales se venden con una mayor frecuencia")


st.divider()
st.header(" 2. Motor de Limpieza")

# PASO A: Eliminar Duplicados (Vimos el ID 2 y 10 repetidos en el CSV)
df = df.drop_duplicates(subset=['id'])

# PASO B: Corregir Tipos de Datos
# El CSV tiene el ID 12 con cantidad "1" entre comillas (texto). Lo forzamos a número.
df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce')

# PASO C: Rellenar Nulos (NaN)
# Si no sabemos la cantidad, asumiremos que se vendió 1 unidad.
df['cantidad'] = df['cantidad'].fillna(1)

st.success(" Limpieza automátizada: Duplicados removidos, números corregidos y nulos rellenados.")
st.dataframe(df)
st.text_area("veo que se realiza una limpieza de los datos, se eliman primero registros duplicados usando dro`p_duplicates() para evitar que los datos sean repetidos y no afecten el analisis, creo que despues se covierte en la columna" \
"cantidad a un formato numerico usando to-numeric para asegurar que los calculos funcionen correctamente,y ya reemplazan con 1 para asumir que almenos se vendio una unidad ")


st.divider()
st.header("✨ 3. Transformación de Reporte")

# Calculamos el subtotal primero
df['Ingreso_Bruto'] = df['precio'] * df['cantidad']

# CREAMOS UNA VISTA LIMPIA PARA EL REPORTE
# Renombramos y ordenamos de mayor ingreso a menor
reporte_ejecutivo = df.rename(columns={
    'id': 'ID Pedido',
    'producto': 'Producto',
    'Ingreso_Bruto': 'Venta Total ($)'
}).sort_values(by='Venta Total ($)', ascending=False)

st.write("Top de ventas del mes (Ordenado):")
st.dataframe(reporte_ejecutivo[['ID Pedido', 'Producto', 'Venta Total ($)']].head(10))
st.text_area("se transportan los datos, para generar un informe ma claro, se calcula el ingreso del bruto multiplicandolo por el precio y por la cantidad vendida, se renombra (creo) algunas columnas para que los nombres sean mas sencillos " \
"de leer o de entrender , por ultimo se ordenan de mayor a menor segun el valor de la venta total ")


st.sidebar.header(" Panel de Auditoría")

# Filtro multi-selección
ciudades_filtro = st.sidebar.multiselect(
    "Filtrar por Tipo:",
    options=df['tipo'].unique(),
    default=df['tipo'].unique()
)

# Filtro Slider
monto_min = st.sidebar.slider("Ver ventas superiores a ($):", 0, 100, 0)

# APLICACIÓN DE LÓGICA FILTRADO (AND)
# Que pertenezca al tipo seleccionado Y supere el monto mínimo
df_final = df[(df['tipo'].isin(ciudades_filtro)) & (df['Ingreso_Bruto'] >= monto_min)]

st.subheader("📋 Pedidos Filtrados")
st.table(df_final)
st.text_area("se crean filtros interactivos para analizar los datos, uno de ellos creo que es para seleccionar uno o varios productos mientras que el otro permite  elegir un monto minimo para la venta , se que ambas e aplican a este dataset para mostrar unicamente pedidos que se cumplen ")


st.divider()
st.header("📈 4. Análisis Agregado")

# Agrupamos por tipo y sumamos ingresos
resumen = df.groupby('tipo')['Ingreso_Bruto'].agg(['sum', 'count', 'mean']).round(2)
st.write(resumen)

st.bar_chart(resumen['sum'])
st.text_area(" se calculan 3 metricas principales, la suma totral de los ingresos, la cantidad de ventas realizadas y el promedio de ingreso")


# Tabla de ejemplo de proveedores
proveedores = pd.DataFrame({
    'producto': ['Espresso', 'Latte', 'Capuccino', 'Muffin', 'Cold Brew', 'Pastel de Chocolate'],
    'Proveedor': ['Granos del Cauca', 'Lácteos Central', 'Lácteos Central', 'Trigo & Sal', 'Refrescantes S.A.', 'Delicias Doña Ana']
})

# Fusión (Merge)
df_maestro = pd.merge(df, proveedores, on='producto', how='left')

st.header("🏢 Contacto de Proveedores por Pedido")
st.dataframe(df_maestro[['id', 'producto', 'Proveedor']])
st.text_area("se combinan dos tablas, una de ellas contiene los proveedores de cada producto")
