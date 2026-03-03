import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="IESE - Liderazgo y Autoconciencia", layout="centered")

# Configuración
RESET_PASSWORD = st.secrets.get("reset_password", "iese2024")  # Cambia "iese2024" por tu contraseña
TIEMPO_VOTACION = 12  # Tiempo en segundos desde el primer voto

# Inicializar datos en memoria (se mantiene mientras la app esté activa)
if 'votos' not in st.session_state:
    st.session_state.votos = pd.DataFrame(columns=["Nick", "Delta"])
if 'timer_inicio' not in st.session_state:
    st.session_state.timer_inicio = None

st.title("📊 Pulso de Autoconciencia EMBA")

# Sidebar con opción de reset (solo para administrador)
with st.sidebar:
    st.markdown("### 🔧 Admin")
    with st.expander("Resetear datos"):
        st.warning("⚠️ Esto borrará todos los votos y el timer")
        password = st.text_input("Contraseña:", type="password", key="reset_pwd")
        if st.button("🗑️ Resetear"):
            if password == RESET_PASSWORD:
                st.session_state.votos = pd.DataFrame(columns=["Nick", "Delta"])
                st.session_state.timer_inicio = None
                st.success("✅ Datos reseteados correctamente")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta")

# --- TIMER DE VOTACIÓN ---
tiempo_restante = None
votacion_cerrada = False

if st.session_state.timer_inicio is not None:
    tiempo_transcurrido = time.time() - st.session_state.timer_inicio
    tiempo_restante = TIEMPO_VOTACION - tiempo_transcurrido

    if tiempo_restante > 0:
        minutos = int(tiempo_restante // 60)
        segundos = int(tiempo_restante % 60)
        st.markdown(f"### ⏱️ Tiempo restante: **{minutos:02d}:{segundos:02d}**")

        # Barra de progreso
        progreso = 1 - (tiempo_restante / TIEMPO_VOTACION)
        st.progress(progreso)

        # Auto-refresh cada 2 segundos mientras el timer está activo
        time.sleep(2)
        st.rerun()
    else:
        st.markdown("### ⏱️ ¡Tiempo finalizado!")
        st.warning("⚠️ La votación ha cerrado. Revisa los resultados abajo.")
        votacion_cerrada = True
else:
    st.info("⏱️ El timer iniciará cuando llegue el primer voto")

st.markdown("---")

if not votacion_cerrada:
    nick = st.text_input("Introduce tu Nick:", placeholder="Ej. Pedro")

    if nick:
        st.markdown(f"### Hola **{nick}**, hagamos memoria...")
        q1 = st.select_slider("Energía y optimismo al iniciar el EMBA (1-10):", options=range(1, 11), value=5)

        st.markdown("### ¿Y cómo te sientes HOY?")
        q2 = st.select_slider("Puntuación actual (1-10):", options=range(1, 11), value=5)

        if st.button("🚀 Enviar y ver resultados del grupo"):
            delta = q2 - q1

            # Iniciar timer si es el primer voto
            if st.session_state.timer_inicio is None:
                st.session_state.timer_inicio = time.time()

            # Agregar el voto a la lista en memoria
            nuevo_voto = pd.DataFrame({"Nick": [nick], "Delta": [delta]})
            st.session_state.votos = pd.concat([st.session_state.votos, nuevo_voto], ignore_index=True)

            # Animación según el resultado
            if delta > 0:
                st.balloons()  # Celebración si mejoró
                st.success(f"🎉 ¡Genial! Tu evolución es de {delta:+} puntos.")
            elif delta < 0:
                st.snow()  # Nieve si empeoró
                st.info(f"💙 Tu evolución es de {delta:+} puntos. Recuerda que todos tenemos altibajos.")
            else:
                st.info(f"Tu evolución es de {delta:+} puntos. Te mantienes estable.")

            time.sleep(2)
            st.rerun()
else:
    st.markdown("### 📝 La votación ha finalizado")
    st.info("Los resultados finales están disponibles más abajo.")

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