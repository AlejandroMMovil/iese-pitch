import streamlit as st
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe, get_as_dataframe
from oauth2client.service_account import ServiceAccountCredentials
import time

st.set_page_config(page_title="IESE - Liderazgo y Autoconciencia", layout="centered")

# URL de tu Google Sheet real
SHEET_URL = "https://docs.google.com/spreadsheets/d/1yYjRPYPnMcunv95syWDCo92beM9iXneX67JUOyMi5W4/edit?usp=sharing"
SHEET_ID = "1yYjRPYPnMcunv95syWDCo92beM9iXneX67JUOyMi5W4"

# Configurar acceso a Google Sheets
@st.cache_resource
def get_gsheet_connection():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    # Intentar con credenciales de Streamlit Secrets
    if "gcp_service_account" in st.secrets:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        gc = gspread.authorize(creds)
    else:
        # Sin credenciales, solo lectura desde CSV público
        return None

    return gc

gc = get_gsheet_connection()
if gc:
    sh = gc.open_by_key(SHEET_ID)
    worksheet = sh.sheet1
else:
    worksheet = None

st.title("📊 Pulso de Autoconciencia EMBA")

nick = st.text_input("Introduce tu Nick:", placeholder="Ej. Pedro")

if nick:
    st.markdown(f"### Hola **{nick}**, hagamos memoria...")
    q1 = st.select_slider("Energía y optimismo al iniciar el EMBA (1-10):", options=range(1, 11), value=5)
    
    st.markdown("### ¿Y cómo te sientes HOY?")
    q2 = st.select_slider("Puntuación actual (1-10):", options=range(1, 11), value=5)

    if st.button("🚀 Enviar y ver resultados del grupo"):
        delta = q2 - q1

        if worksheet is None:
            st.error("⚠️ No hay credenciales configuradas. Contacta al administrador.")
            st.info("El administrador debe configurar 'gcp_service_account' en los Secrets de Streamlit Cloud.")
        else:
            try:
                # Leer datos actuales para no borrar lo anterior
                df_actual = get_as_dataframe(worksheet, evaluate_formulas=True)
                df_actual = df_actual.dropna(how='all')  # Eliminar filas completamente vacías

                # Si está vacío, inicializar con columnas
                if df_actual.empty or 'Nick' not in df_actual.columns:
                    df_actual = pd.DataFrame(columns=["Nick", "Delta"])

                # Crear nueva fila y subirla
                new_data = pd.DataFrame({"Nick": [nick], "Delta": [delta]})
                df_final = pd.concat([df_actual, new_data], ignore_index=True)

                # Actualizar el sheet
                set_with_dataframe(worksheet, df_final)

                st.balloons() # Pequeña celebración visual
                st.success(f"¡Hecho! Tu evolución es de {delta:+} puntos.")
                time.sleep(2)
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar: {str(e)}")
                st.info("Verifica que el Google Sheet esté configurado como público y permita edición.")

# --- RANKING GLOBAL ---
st.markdown("---")
st.subheader("Así evoluciona nuestra clase:")

# Botón manual para refrescar el ranking en directo durante el discurso
if st.button("🔄 Actualizar Ranking"):
    if worksheet is None:
        # Leer desde CSV público como fallback
        csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
        try:
            df_global = pd.read_csv(csv_url)
            df_global = df_global.dropna(how='all')

            if not df_global.empty and 'Delta' in df_global.columns:
                df_sorted = df_global.sort_values(by="Delta", ascending=False)
                st.table(df_sorted)
                st.info("💡 Recuerda, siempre hay alguien en un punto parecido al tuyo.")
            else:
                st.write("Aún no hay votos. ¡Sé el primero!")
        except Exception as e:
            st.error(f"No se pudo leer el sheet: {str(e)}")
    else:
        try:
            df_global = get_as_dataframe(worksheet, evaluate_formulas=True)
            df_global = df_global.dropna(how='all')  # Eliminar filas vacías

            if not df_global.empty and 'Delta' in df_global.columns:
                # Ordenar por el mayor cambio (Delta)
                df_sorted = df_global.sort_values(by="Delta", ascending=False)
                st.table(df_sorted)
                st.info("💡 Recuerda, siempre hay alguien en un punto parecido al tuyo.")
            else:
                st.write("Aún no hay votos. ¡Sé el primero!")
        except Exception as e:
            st.error(f"Error al leer datos: {str(e)}")