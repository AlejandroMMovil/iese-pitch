import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="IESE - Liderazgo y Autoconciencia", layout="centered")

# Inicializar datos en memoria (se mantiene mientras la app esté activa)
if 'votos' not in st.session_state:
    st.session_state.votos = pd.DataFrame(columns=["Nick", "Delta"])

st.title("📊 Pulso de Autoconciencia EMBA")

nick = st.text_input("Introduce tu Nick:", placeholder="Ej. Pedro")

if nick:
    st.markdown(f"### Hola **{nick}**, hagamos memoria...")
    q1 = st.select_slider("Energía y optimismo al iniciar el EMBA (1-10):", options=range(1, 11), value=5)
    
    st.markdown("### ¿Y cómo te sientes HOY?")
    q2 = st.select_slider("Puntuación actual (1-10):", options=range(1, 11), value=5)

    if st.button("🚀 Enviar y ver resultados del grupo"):
        delta = q2 - q1

        # Agregar el voto a la lista en memoria
        nuevo_voto = pd.DataFrame({"Nick": [nick], "Delta": [delta]})
        st.session_state.votos = pd.concat([st.session_state.votos, nuevo_voto], ignore_index=True)

        st.balloons() # Pequeña celebración visual
        st.success(f"¡Hecho! Tu evolución es de {delta:+} puntos.")
        time.sleep(2)
        st.rerun()

# --- RANKING GLOBAL ---
st.markdown("---")
st.subheader("Así evoluciona nuestra clase:")

# Mostrar ranking automáticamente (siempre visible)
if not st.session_state.votos.empty:
    st.markdown(f"**Total de votos:** {len(st.session_state.votos)}")

    # Ordenar por el mayor cambio (Delta)
    df_sorted = st.session_state.votos.sort_values(by="Delta", ascending=False)
    st.table(df_sorted)
    st.info("💡 Recuerda, siempre hay alguien en un punto parecido al tuyo.")
else:
    st.write("Aún no hay votos. ¡Sé el primero!")