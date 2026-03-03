import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="IESE - Liderazgo y Autoconciencia", layout="centered")

# Configuración
RESET_PASSWORD = st.secrets.get("reset_password", "iese2024")  # Cambia "iese2024" por tu contraseña
TIEMPO_VOTACION = 20  # Tiempo en segundos desde el primer voto

# Almacenamiento compartido entre TODOS los usuarios
@st.cache_resource
def get_shared_data():
    return {
        'votos': pd.DataFrame(columns=["Nick", "Delta"]),
        'timer_inicio': None
    }

shared = get_shared_data()

# Mantener también en session_state para tracking local
if 'mi_voto' not in st.session_state:
    st.session_state.mi_voto = None

st.title("📊 Pulso de Autoconciencia EMBA")

# Sidebar con opción de reset (solo para administrador)
with st.sidebar:
    st.markdown("### 🔧 Admin")
    with st.expander("Resetear datos"):
        st.warning("⚠️ Esto borrará todos los votos y el timer")
        password = st.text_input("Contraseña:", type="password", key="reset_pwd")
        if st.button("🗑️ Resetear"):
            if password == RESET_PASSWORD:
                shared['votos'] = pd.DataFrame(columns=["Nick", "Delta"])
                shared['timer_inicio'] = None
                st.session_state.mi_voto = None
                st.success("✅ Datos reseteados correctamente")
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta")

# --- TIMER DE VOTACIÓN ---
tiempo_restante = None
votacion_cerrada = False

if shared['timer_inicio'] is not None:
    tiempo_transcurrido = time.time() - shared['timer_inicio']
    tiempo_restante = TIEMPO_VOTACION - tiempo_transcurrido

    if tiempo_restante > 0:
        minutos = int(tiempo_restante // 60)
        segundos = int(tiempo_restante % 60)
        st.markdown(f"### ⏱️ Tiempo restante: **{minutos:02d}:{segundos:02d}**")

        # Barra de progreso
        progreso = 1 - (tiempo_restante / TIEMPO_VOTACION)
        st.progress(progreso)

        # Auto-refresh SOLO si ya voté (para no bloquear a los demás)
        if st.session_state.mi_voto is not None and tiempo_restante > 1:
            time.sleep(1)
            st.rerun()
    else:
        st.markdown("### ⏱️ ¡Tiempo finalizado!")
        st.warning("⚠️ La votación ha cerrada. Revisa los resultados abajo.")
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
            # Verificar si el tiempo ya expiró (para usuarios que no han recargado)
            if shared['timer_inicio'] is not None:
                tiempo_transcurrido = time.time() - shared['timer_inicio']
                if tiempo_transcurrido > TIEMPO_VOTACION:
                    st.error("⏱️ ¡Tiempo finalizado! Ya no se pueden enviar más votos.")
                    st.info("Refresca la página para ver los resultados finales.")
                    st.rerun()
                    st.stop()  # Detener ejecución aquí

            delta = q2 - q1

            # Iniciar timer si es el primer voto
            if shared['timer_inicio'] is None:
                shared['timer_inicio'] = time.time()

            # Agregar el voto a la lista compartida
            nuevo_voto = pd.DataFrame({"Nick": [nick], "Delta": [delta]})
            shared['votos'] = pd.concat([shared['votos'], nuevo_voto], ignore_index=True)

            # Guardar mi voto en session_state
            st.session_state.mi_voto = delta

            # Animación según el resultado
            if delta > 0:
                st.balloons()  # Celebración si mejoró
                st.success(f"🎉 ¡Genial! Tu evolución es de {delta:+} puntos.")
            elif delta < 0:
                st.snow()  # Nieve si empeoró
                st.info(f"💙 Tu evolución es de {delta:+} puntos. Recuerda que todos tenemos altibajos.")
            else:
                st.info(f"Tu evolución es de {delta:+} puntos. Te mantienes estable.")

            # Rerun SIN sleep para no bloquear a otros usuarios
            st.rerun()
else:
    st.markdown("### 📝 La votación ha finalizado")
    st.info("Los resultados finales están disponibles más abajo.")

# --- RANKING GLOBAL ---
st.markdown("---")
st.subheader("Así evoluciona nuestra clase:")

# Mostrar ranking automáticamente (siempre visible)
if not shared['votos'].empty:
    st.markdown(f"**Total de votos:** {len(shared['votos'])}")

    # Ordenar por el mayor cambio (Delta)
    df_sorted = shared['votos'].sort_values(by="Delta", ascending=False).reset_index(drop=True)

    # Si el usuario ya votó, mostrar contexto personalizado
    if st.session_state.mi_voto is not None:
        mi_delta = st.session_state.mi_voto

        # Encontrar usuarios cercanos (5 por arriba, 5 por abajo)
        df_superiores = df_sorted[df_sorted['Delta'] > mi_delta].tail(5)  # 5 mejores que yo
        df_inferiores = df_sorted[df_sorted['Delta'] < mi_delta].head(5)  # 5 peores que yo
        mi_fila = df_sorted[df_sorted['Delta'] == mi_delta]

        # Combinar y ordenar
        df_contexto = pd.concat([df_superiores, mi_fila, df_inferiores]).sort_values(by="Delta", ascending=False).reset_index(drop=True)

        st.markdown("### 👥 Compañeros con resultados similares:")
        st.table(df_contexto)

        # Opción para ver todos
        if st.button("📊 Ver ranking completo"):
            st.markdown("### 📋 Ranking completo:")
            st.table(df_sorted)
    else:
        # Si no ha votado, mostrar todos
        st.table(df_sorted)

    st.info("💡 Recuerda, siempre hay alguien en un punto parecido al tuyo.")
else:
    st.write("Aún no hay votos. ¡Sé el primero!")