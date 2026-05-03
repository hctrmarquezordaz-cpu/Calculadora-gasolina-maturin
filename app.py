import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib3
import pandas as pd
from datetime import datetime

# ---------------------------------------------------------
# CONFIGURACIÓN GENERAL Y ESTILOS (MODO CLARO / BLANCO)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Gasolina VZLA Inteligente",
    page_icon="⛽",
    layout="centered"
)

# Constante de precio de gasolina
PRECIO_USD_LITRO = 0.50

# CSS Avanzado para Modo Claro (Blanco y Verde)
st.markdown("""
    <style>
    /* Fondo general blanco */
    .stApp {
        background-color: #ffffff;
        color: #212529;
    }
    
    /* Contenedores de Tarjetas (Cards) */
    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #e9ecef;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
        transition: transform 0.2s;
    }
    
    /* Efecto al tocar */
    div[data-testid="metric-container"]:active {
        transform: scale(0.98);
        border-color: #198754;
    }

    /* Estilo de los Números (Verde) */
    div[data-testid="stMetricValue"] {
        color: #198754 !important; 
        font-size: 2.3rem !important;
        font-weight: 900 !important;
    }
    
    /* Estilo de las Etiquetas de los números */
    div[data-testid="stMetricLabel"] {
        color: #6c757d !important;
        font-size: 1rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Títulos y Subtítulos Centrados y Oscuros */
    h1, h2, h3, .stMarkdown p {
        text-align: center;
        color: #212529;
    }

    /* Banner de Información (Verde claro) */
    .stAlert {
        background-color: #d1e7dd !important;
        color: #0f5132 !important;
        border: 1px solid #badbcc !important;
        border-radius: 10px;
    }
    
    /* Botones */
    .stButton>button {
        background-color: #ffffff !important;
        color: #198754 !important;
        border: 2px solid #198754 !important;
        border-radius: 20px !important;
        transition: all 0.3s !important;
        font-weight: bold;
    }
    .stButton>button:hover, .stButton>button:active {
        background-color: #198754 !important;
        color: #ffffff !important;
        box-shadow: 0px 4px 10px rgba(25, 135, 84, 0.2);
    }
    
    /* Inputs y Selectores */
    .stNumberInput input, .stTextInput input {
        background-color: #ffffff !important;
        color: #212529 !important;
        border: 1px solid #ced4da !important;
    }
    </style>
""", unsafe_allow_html=True)

# Desactivar advertencias de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@st.cache_data(ttl=3600)
def obtener_tasa_bcv():
    url = "https://www.bcv.org.ve/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        respuesta = requests.get(url, headers=headers, verify=False, timeout=15)
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        dolar_div = soup.find('div', id='dolar')
        if dolar_div:
            tasa_texto = dolar_div.find('strong').text.strip()
            return float(tasa_texto.replace(',', '.'))
    except Exception:
        return None
    return None

# ---------------------------------------------------------
# INTERFAZ PRINCIPAL
# ---------------------------------------------------------
st.markdown("<h1>⛽ Gasolina VZLA</h1>", unsafe_allow_html=True)
st.markdown("<h3>Calculadora Inteligente</h3>", unsafe_allow_html=True)
st.write("") 

tasa = obtener_tasa_bcv()
ahora = datetime.now().strftime("%d/%m/%Y, %I:%M %p")

if tasa:
    st.info(f"🟢 **Tasa Oficial BCV:** Bs. {tasa:.2f}")
    
    st.markdown("---")
    
    # Selector de Modo (Normal vs Inverso)
    modo = st.radio(
        "Selecciona el modo de cálculo:",
        ("Normal (Calcular por Litros)", "Inverso (Tengo $ fijos)"),
        horizontal=True
    )
    
    litros_a_surtir = 0.0
    total_usd = 0.0
    total_bs = 0.0
    
    st.write("")

    if "Normal" in modo:
        # MODO NORMAL: Litros -> USD/Bs
        st.markdown("#### MODO NORMAL")
        litros_entrada = st.number_input(
            "¿Cuántos litros vas a surtir? (L)", 
            min_value=1.0, max_value=200.0, value=1.0, step=1.0
        )
        litros_a_surtir = litros_entrada
        total_usd = litros_a_surtir * PRECIO_USD_LITRO
        total_bs = total_usd * tasa
        
    else:
        # MODO INVERSO: USD -> Litros/Bs
        st.markdown("#### MODO INVERSO")
        usd_entrada = st.number_input(
            "¿Cuántos dólares ($) tienes?", 
            min_value=1.0, max_value=100.0, value=10.0, step=1.0
        )
        total_usd = usd_entrada
        # Cálculo inverso: Litros = Dólares / 0.50
        litros_a_surtir = total_usd / PRECIO_USD_LITRO
        total_bs = total_usd * tasa

    st.markdown("---")
    st.markdown("#### RESULTADOS")
    
    # Mostrar resultados en tarjetas destacadas
    col1, col2 = st.columns(2)
    
    if "Normal" in modo:
        with col1:
            st.metric(label="Total USD", value=f"$ {total_usd:.2f}")
        with col2:
            st.metric(label="Total Bolívares", value=f"Bs. {total_bs:.2f}")
    else:
        with col1:
            st.metric(label="Litros a surtir", value=f"{litros_a_surtir:.1f} L")
        with col2:
            st.metric(label="Total Bolívares", value=f"Bs. {total_bs:.2f}")
            
    st.markdown("---")
    
    # Tabla de referencia rápida (Adaptada)
    st.markdown("### 📊 Referencia Rápida ($0.50/L)")
    if "Normal" in modo:
        referencias = [10, 20, 30, 40]
        data_ref = {
            "Litros": [f"{l} L" for l in referencias],
            "Dólares": [f"$ {l*PRECIO_USD_LITRO:.2f}" for l in referencias],
            "Bolívares": [f"Bs. {l*PRECIO_USD_LITRO*tasa:.2f}" for l in referencias]
        }
    else:
        # Referencias por billetes comunes
        billetes = [5, 10, 20, 50]
        data_ref = {
            "Tengo ($)": [f"$ {b}.00" for b in billetes],
            "Surtiré (L)": [f"{b/PRECIO_USD_LITRO:.1f} L" for b in billetes],
            "Pagaré (Bs.)": [f"Bs. {b*tasa:.2f}" for b in billetes]
        }
        
    st.dataframe(pd.DataFrame(data_ref), use_container_width=True, hide_index=True)

else:
    st.error("⚠️ No se pudo obtener la tasa automática del BCV. Verifique su conexión.")
    tasa_manual = st.number_input("Introduzca la tasa manualmente para calcular:", min_value=0.0, format="%.2f")
    if tasa_manual > 0:
        litros = st.number_input("Cantidad de litros:", min_value=0.1, value=1.0)
        st.warning(f"Total a pagar: $ {litros*0.50:.2f}  |  Bs. {litros*0.50*tasa_manual:.2f}")

st.write("")
st.caption(f"Última actualización de tasa: {ahora}. Los datos provienen del BCV.")
col1, col2, col3 = st.columns([1,3,1])
with col2:
    if st.button("🔄 Actualizar Tasa del Día", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
        /* Fondo general */
    .stApp {{
        background-color: #0e1117;
        background-image: radial-gradient(circle at 50% 0%, #1a2236 0%, #0e1117 80%);
        color: #ffffff;
    }}
    
    /* Contenedores de Tarjetas (Cards) */
    div[data-testid="metric-container"] {{
        background: rgba(28, 36, 54, 0.8);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(0, 255, 136, 0.1);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        text-align: center;
        transition: transform 0.2s;
    }}
    
    /* Efecto al tocar */
    div[data-testid="metric-container"]:active {{
        transform: scale(0.98);
        border-color: #00ff88;
    }}

    /* Estilo de los Números (Verde Neón Brillante) */
    div[data-testid="stMetricValue"] {{
        color: #00ff88 !important; 
        font-size: 2.3rem !important;
        font-weight: 900 !important;
        text-shadow: 0px 0px 12px rgba(0, 255, 136, 0.5);
    }}
    
    /* Estilo de las Etiquetas de los números */
    div[data-testid="stMetricLabel"] {{
        color: #8fa1b3 !important;
        font-size: 1rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    /* Títulos y Subtítulos Centrados */
    h1, h2, h3, .stMarkdown p {{
        text-align: center;
        color: #ffffff;
    }}

    /* Banner de Información (Verde) */
    .stAlert {{
        background-color: rgba(0, 255, 136, 0.1) !important;
        color: #00ff88 !important;
        border: 1px solid #00ff88 !important;
        border-radius: 10px;
    }}
    
    /* Botones Neón */
    .stButton>button {{
        background-color: transparent !important;
        color: #ffffff !important;
        border: 2px solid #ffffff !important;
        border-radius: 20px !important;
        transition: all 0.3s !important;
    }}
    .stButton>button:hover, .stButton>button:active {{
        border-color: #00ff88 !important;
        color: #00ff88 !important;
        box-shadow: 0px 0px 10px rgba(0, 255, 136, 0.3);
    }}
    </style>
""", unsafe_allow_html=True)

# Desactivar advertencias de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@st.cache_data(ttl=3600)
def obtener_tasa_bcv():
    url = "https://www.bcv.org.ve/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        respuesta = requests.get(url, headers=headers, verify=False, timeout=15)
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        dolar_div = soup.find('div', id='dolar')
        if dolar_div:
            tasa_texto = dolar_div.find('strong').text.strip()
            return float(tasa_texto.replace(',', '.'))
    except Exception:
        return None
    return None

# ---------------------------------------------------------
# INTERFAZ PRINCIPAL
# ---------------------------------------------------------
st.markdown("<h1>⛽ Gasolina VZLA</h1>", unsafe_allow_html=True)
st.markdown("<h3>Calculadora Inteligente</h3>", unsafe_allow_html=True)
st.write("") 

tasa = obtener_tasa_bcv()
ahora = datetime.now().strftime("%d/%m/%Y, %I:%M %p")

if tasa:
    st.info(f"🟢 **Tasa Oficial BCV:** Bs. {tasa:.2f}")
    
    st.markdown("---")
    
    # NUEVO: Selector de Modo (Normal vs Inverso)
    modo = st.radio(
        "Selecciona el modo de cálculo:",
        ("Normal (Calcular por Litros)", "Inverso (Tengo $ fijos)"),
        horizontal=True
    )
    
    litros_a_surtir = 0.0
    total_usd = 0.0
    total_bs = 0.0
    
    st.write("")

    if "Normal" in modo:
        # MODO NORMAL: Litros -> USD/Bs
        st.markdown("#### MODO NORMAL")
        litros_entrada = st.number_input(
            "¿Cuántos litros vas a surtir? (L)", 
            min_value=1.0, max_value=200.0, value=1.0, step=1.0
        )
        litros_a_surtir = litros_entrada
        total_usd = litros_a_surtir * PRECIO_USD_LITRO
        total_bs = total_usd * tasa
        
    else:
        # MODO INVERSO: USD -> Litros/Bs
        st.markdown("#### MODO INVERSO")
        usd_entrada = st.number_input(
            "¿Cuántos dólares ($) tienes?", 
            min_value=1.0, max_value=100.0, value=10.0, step=1.0
        )
        total_usd = usd_entrada
        # Cálculo inverso: Litros = Dólares / 0.50
        litros_a_surtir = total_usd / PRECIO_USD_LITRO
        total_bs = total_usd * tasa

    st.markdown("---")
    st.markdown("#### RESULTADOS")
    
    # Mostrar resultados en tarjetas destacadas
    col1, col2 = st.columns(2)
    
    # En Modo Inverso, resaltamos los Litros. En Normal, los Bolívares.
    if "Normal" in modo:
        with col1:
            st.metric(label="Total USD", value=f"$ {total_usd:.2f}")
        with col2:
            st.metric(label="Total Bolívares", value=f"Bs. {total_bs:.2f}")
    else:
        with col1:
            st.metric(label="Litros a surtir", value=f"{litros_a_surtir:.1f} L")
        with col2:
            st.metric(label="Total Bolívares", value=f"Bs. {total_bs:.2f}")
            
    st.markdown("---")
    
    # Tabla de referencia rápida (Adaptada)
    st.markdown("### 📊 Referencia Rápida ($0.50/L)")
    if "Normal" in modo:
        referencias = [10, 20, 30, 40]
        data_ref = {
            "Litros": [f"{l} L" for l in referencias],
            "Dólares": [f"$ {l*PRECIO_USD_LITRO:.2f}" for l in referencias],
            "Bolívares": [f"Bs. {l*PRECIO_USD_LITRO*tasa:.2f}" for l in referencias]
        }
    else:
        # Referencias por billetes comunes
        billetes = [5, 10, 20, 50]
        data_ref = {
            "Tengo ($)": [f"$ {b}.00" for b in billetes],
            "Surtiré (L)": [f"{b/PRECIO_USD_LITRO:.1f} L" for b in billetes],
            "Pagaré (Bs.)": [f"Bs. {b*tasa:.2f}" for b in billetes]
        }
        
    st.dataframe(pd.DataFrame(data_ref), use_container_width=True, hide_index=True)

else:
    st.error("⚠️ No se pudo obtener la tasa automática del BCV. Verifique su conexión.")
    # (Lógica manual omitida para brevedad, pero sigue igual)

st.write("")
st.caption(f"Última actualización de tasa: {ahora}. Los datos provienen del BCV.")
col1, col2, col3 = st.columns([1,3,1])
with col2:
    if st.button("🔄 Actualizar Tasa del Día", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
        
