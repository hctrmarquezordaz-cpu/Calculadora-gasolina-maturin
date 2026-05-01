import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib3
import pandas as pd

# Configuración de la página para dispositivos móviles y escritorio
st.set_page_config(
    page_title="Gasolina VZLA - Calculadora BCV",
    page_icon="⛽",
    layout="centered"
)

# Estilo personalizado para mejorar la visibilidad en el sol (estaciones de servicio)
st.markdown('''
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    ''', unsafe_allow_html=True)

# Desactivar advertencias de SSL para el portal del BCV
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@st.cache_data(ttl=3600) # Caché por 1 hora para no saturar el BCV
def obtener_tasa_bcv():
    url = "https://www.bcv.org.ve/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        respuesta = requests.get(url, headers=headers, verify=False, timeout=15)
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        # Buscar el contenedor de Dólar
        dolar_div = soup.find('div', id='dolar')
        if dolar_div:
            tasa_texto = dolar_div.find('strong').text.strip()
            return float(tasa_texto.replace(',', '.'))
    except Exception as e:
        return None
    return None

# Título y encabezado
st.title("⛽ Gasolina VZLA")
st.subheader("Calculadora de Pago (Tasa BCV)")

tasa = obtener_tasa_bcv()

if tasa:
    st.success(f"Tasa Oficial BCV: **Bs. {tasa:.2f}**")
    
    # Sección de entrada
    col_input, col_info = st.columns([2, 1])
    with col_input:
        litros = st.number_input("Cantidad de litros:", min_value=0.1, max_value=200.0, value=40.0, step=1.0)
    with col_info:
        precio_fijo = st.text_input("Precio/Litro (USD):", value="0.50", disabled=True)
    
    # Cálculos
    total_usd = litros * 0.50
    total_bs = total_usd * tasa
    
    # Mostrar resultados destacados
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.metric(label="Total a pagar (USD)", value=f"$ {total_usd:.2f}")
    with c2:
        st.metric(label="Total a pagar (Bolívares)", value=f"Bs. {total_bs:.2f}")
    
    # Tabla de referencia rápida para Maturín o cualquier otra ciudad
    st.markdown("### 📊 Tabla de Referencia Rápida")
    referencias = [10, 20, 30, 40, 50, 60]
    data_ref = {
        "Litros": [f"{l} L" for l in referencias],
        "Dólares ($)": [f"$ {l*0.50:.2f}" for l in referencias],
        "Bolívares (Bs.)": [f"Bs. {l*0.50*tasa:.2f}" for l in referencias]
    }
    st.table(pd.DataFrame(data_ref))

else:
    st.error("⚠️ No se pudo obtener la tasa automática del BCV.")
    tasa_manual = st.number_input("Introduzca la tasa manualmente para calcular:", min_value=0.0, format="%.2f")
    if tasa_manual > 0:
        litros = st.number_input("Cantidad de litros:", min_value=0.1, value=40.0)
        st.info(f"Total: $ {litros*0.50:.2f} / Bs. {litros*0.50*tasa_manual:.2f}")

st.markdown("---")
st.caption("Nota: Los datos se actualizan automáticamente desde el sitio oficial del BCV.")
if st.button("🔄 Actualizar Tasa"):
    st.cache_data.clear()
    st.rerun()