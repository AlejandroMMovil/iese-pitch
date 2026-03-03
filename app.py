import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="IESE - Self-Awareness Test", layout="centered")

# Estilo para fondo oscuro y letra llamativa
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stSlider { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

if 'responses' not in st.session_state:
    st.session_state.responses = pd.DataFrame(columns=['Nick', 'Delta'])

st.header("Análisis de Autoconciencia")

nick = st.text_input("Introduce tu nombre o nick:", placeholder="Ej. Pedro")

if nick:
    st.write(f"### Hola {nick}, visualízate hace dos años, cuando entraste al EMBA:")
    q1 = st.select_slider("¿Cómo valorarías tu energía y optimismo en ese momento?", options=range(1, 11), value=5, key="q1")
    
    st.write("### ¿Y cómo te puntuarías HOY?")
    q2 = st.select_slider("Puntuación actual:", options=range(1, 11), value=5, key="q2")

    if st.button("Enviar y Ver Resultados"):
        delta = q2 - q1
        new_row = pd.DataFrame({'Nick': [nick], 'Delta': [delta]})
        st.session_state.responses = pd.concat([st.session_state.responses, new_row]).drop_duplicates('Nick', keep='last')
        
        # Mensaje temporal que desaparece
        placeholder = st.empty()
        signo = "+" if delta > 0 else ""
        placeholder.success(f"¡Has registrado un cambio de {signo}{delta} puntos!")
        time.sleep(3)
        placeholder.empty()

        # Mostrar Ranking Final
        st.markdown("---")
        st.subheader("Así están tus compañeros:")
        df_display = st.session_state.responses.sort_values(by='Delta', ascending=False)
        st.table(df_display)
        
        st.markdown("#### *Siempre hay gente en un punto parecido al tuyo*")

# Botón de reset para tus simulacros (en el menú lateral)
if st.sidebar.button("Resetear Simulacro"):
    st.session_state.responses = pd.DataFrame(columns=['Nick', 'Delta'])
    st.rerun()