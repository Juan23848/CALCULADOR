
import streamlit as st
import pandas as pd

# ------------------------
# CONFIGURACIÓN INICIAL
# ------------------------

VI_ABRIL = 85.056195
VI_MAYO = VI_ABRIL * 1.03

GREMIOS = {
    "AMET": 0.015,
    "SUTEF": 0.02,
    "SUETRA": 0.02,
    "ATE": 0.022,
    "UDAF": 0.013,
    "UDA": 0.015,
    "UPCN": 0.022
}

# ------------------------
# CARGA DE DATOS
# ------------------------

@st.cache_data
def cargar_puntajes():
    return pd.read_excel("Simulador_Salarial_Cargos_Abril2025.xlsx", sheet_name="Simulador Abril 2025")

df_cargos = cargar_puntajes()

# ------------------------
# FUNCIONES DE CÁLCULO
# ------------------------

def calcular_basico(puntaje, vi):
    return puntaje * vi

def calcular_gremial(descuentos, total_remun, foid):
    total = 0
    for gremio in descuentos:
        if gremio in GREMIOS:
            porcentaje = GREMIOS[gremio]
            total += porcentaje * (total_remun + foid)
    return total

def calcular_total(puntaje, vi, descuentos):
    basico = calcular_basico(puntaje, vi)
    antiguedad = basico * 0.2
    zona = basico * 0.3
    transformacion = basico * 0.08
    foid = 3000  # Valor fijo de ejemplo

    total_remun = basico + antiguedad + zona + transformacion
    total_bruto = total_remun + foid
    total_desc = calcular_gremial(descuentos, total_remun, foid)
    neto = total_bruto - total_desc

    return {
        "Basico": basico,
        "Antiguedad": antiguedad,
        "Zona": zona,
        "Transformacion": transformacion,
        "FOID": foid,
        "Remunerativo": total_remun,
        "Descuento Gremial": total_desc,
        "Neto": neto
    }

# ------------------------
# INTERFAZ STREAMLIT
# ------------------------

st.title("Comparador Salarial Abril vs Mayo 2025")

cargo_seleccionado = st.selectbox("Seleccionar cargo:", df_cargos["CARGO"])
puntaje = df_cargos[df_cargos["CARGO"] == cargo_seleccionado]["PUNTAJE 04/2025"].values[0]

gremio1 = st.selectbox("Gremio 1:", ["Ninguno"] + list(GREMIOS.keys()))
gremio2 = st.selectbox("Gremio 2:", ["Ninguno"] + list(GREMIOS.keys()))

descuentos = []
if gremio1 != "Ninguno": descuentos.append(gremio1)
if gremio2 != "Ninguno" and gremio2 != gremio1: descuentos.append(gremio2)

abril = calcular_total(puntaje, VI_ABRIL, descuentos)
mayo = calcular_total(puntaje, VI_MAYO, descuentos)

resultado = pd.DataFrame({
    "Concepto": abril.keys(),
    "Abril ($)": abril.values(),
    "Mayo ($)": mayo.values(),
    "Diferencia ($)": [mayo[k] - abril[k] for k in abril],
    "Variación (%)": [((mayo[k] - abril[k]) / abril[k] * 100) if abril[k] != 0 else 0 for k in abril]
})

st.dataframe(resultado.style.format(subset=["Abril ($)", "Mayo ($)", "Diferencia ($)"], formatter="{:,.2f}").format({"Variación (%)": "{:+.2f}%"}))
