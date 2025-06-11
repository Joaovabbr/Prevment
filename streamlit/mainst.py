import streamlit as st
from pathlib import Path
import pandas as pd
import sqlite3
import plotly.express as px

marca = 'Insper'

def login_page():
    st.markdown("## 🔐 Login")
    st.write("Acesse nossa plataforma de reputação!")

    with st.form("login_form"):
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")

    if submit:
        dominio = email.split("@")[-1] if "@" in email else ""
        if dominio == "al.insper.edu.br" and senha == "1111":
            st.success("✅ Login realizado com sucesso!")
            st.session_state["logado"] = True
            st.rerun()  
        else:
            st.error("❌ Email ou senha incorretos.")

    st.markdown("[Esqueci minha senha](#)")

def header():
    script_dir = Path(__file__).parent
    logo_path = script_dir / "assets" / f"{marca}_logo.png"

    col_title, col_logo = st.columns([4, 1])

    with col_title:
        st.markdown(f"""
            <div style="font-size:40px; font-weight:600; color:#000000; padding-top:10px;">
                {marca} - Monitoramento de Reputação
            </div>
            <hr style="border:1px solid #e6e6e6; margin-top:10px; margin-bottom:10px;">
        """, unsafe_allow_html=True)

    with col_logo:
        st.image(str(logo_path), width=100, use_container_width=False)

def get_score_data():
    try:
        script_dir = Path(__file__).parent   
        db_path = script_dir.parent / "geral" / "dbs_union.db"
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM entity_med", conn)
        return df
    finally:
        if 'conn' in locals() and conn:
            conn.close()

def cor_gradiente(score, minimo, maximo):
    norm = (score - minimo) / (maximo - minimo)
    if norm <= 0.5:
        r = 255
        g = int(255 * (norm / 0.5))
        b = 0
    else:
        r = int(255 * (1 - (norm - 0.5) / 0.5))
        g = 255
        b = 0
    return f"rgb({r},{g},{b})"

def farol_component(df, marca):
    row = df[df["entity"] == marca].iloc[0]
    score = row["normal_score"]
    min_score = df["normal_score"].min()
    max_score = df["normal_score"].max()
    cor = cor_gradiente(score, min_score, max_score)

    st.markdown(f"""
        <div style='text-align:left; padding:20px; border-radius:10px; background-color:#f5f5f5; width:200px;'>
            <div style='font-size:24px; font-weight:bold; margin-bottom:10px;'>Reputação Atual</div>
            <div style='font-size:100px; color:{cor}; line-height:0.8;'>●</div>
            <div style='font-size:22px; font-weight:bold;'>Score: {score:.2f} / 10</div>
        </div>
    """, unsafe_allow_html=True)

def grafico_comparativo(df):
    df_sorted = df.sort_values(by="normal_score", ascending=True)

    fig = px.bar(df_sorted, x="normal_score", y="entity", orientation="h",
                 labels={"normal_score": "Score Normalizado", "entity": "Marca"},
                 title="Comparação de Reputação entre Marcas",
                 color="normal_score",
                 color_continuous_scale=["red", "yellow", "green"])
    fig.update_layout(coloraxis_showscale=False, height=500)
    return fig

def dashboard_page():
    header()
    st.write("")

    df = get_score_data()
    if df.empty:
        st.error("Dados não encontrados ou banco vazio.")
        return

    col1, col2 = st.columns([1,3])
    with col1:
        farol_component(df, marca)

    with col2:
        fig = grafico_comparativo(df)
        st.plotly_chart(fig, use_container_width=True)

    if st.button("Sair"):
        st.session_state["logado"] = False
        st.rerun()

def main():
    st.set_page_config(page_title="Reputação da Marca", layout="wide")

    if "logado" not in st.session_state:
        st.session_state["logado"] = False

    if st.session_state["logado"]:
        dashboard_page()
    else:
        login_page()

if __name__ == "__main__":
    main()
