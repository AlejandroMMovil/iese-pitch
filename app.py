import streamlit as st
import pandas as pd
from st_gsheets_connection import GSheetsConnection
import time

st.set_page_config(page_title="IESE - Liderazgo y Autoconciencia", layout="centered")

# URL de tu Google Sheet real
SHEET_URL = "https://docs.google.com/spreadsheets/d/1yYjRPYPnMcunv95syWDCo92beM9iXneX67JUOyMi5W4/edit?usp=sharing"

# Establecer conexión
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📊 Pulso de Autoconciencia EMBA")

nick = st.text_input("Introduce tu Nick:", placeholder="Ej. Pedro")

if nick:
    st.markdown(f"### Hola **{nick}**, hagamos memoria...")
    q1 = st.select_slider("Energía y optimismo al iniciar el EMBA (1-10):", options=range(1, 11), value=5)
    
    st.markdown("### ¿Y cómo te sientes HOY?")
    q2 = st.select_slider("Puntuación actual (1-10):", options=range(1, 11), value=5)

    if st.button("🚀 Enviar y ver resultados del grupo"):
        delta = q2 - q1
        
        # Leer datos actuales para no borrar lo anterior
        df_actual = conn.read(spreadsheet=SHEET_URL, usecols=[0,1], ttl=0)
        
        # Crear nueva fila y subirla
        new_data = pd.DataFrame({"Nick": [nick], "Delta": [delta]})
        df_final = pd.concat([df_actual, new_data], ignore_index=True)
        
        conn.update(spreadsheet=SHEET_URL, data=df_final)
        
        st.balloons() # Pequeña celebración visual
        st.success(f"¡Hecho! Tu evolución es de {delta:+} puntos.")
        time.sleep(2)
        st.rerun()

# --- RANKING GLOBAL ---
st.markdown("---")
st.subheader("Así evoluciona nuestra clase:")

# Botón manual para refrescar el ranking en directo durante el discurso
if st.button("🔄 Actualizar Ranking"):
    df_global = conn.read(spreadsheet=SHEET_URL, ttl=0)
    if not df_global.empty:
        # Ordenar por el mayor cambio (Delta)
        df_sorted = df_global.sort_values(by="Delta", ascending=False)
        st.table(df_sorted)
        st.info("💡 Recuerda, siempre hay alguien en un punto parecido al tuyo.")
    else:
        st.write("Aún no hay votos. ¡Sé el primero!")