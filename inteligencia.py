"""ME07: pergunta -> camada semântica -> Gemini -> resposta."""
import os
from pathlib import Path
import pandas as pd
import pandasai as pai
import streamlit as st
from dotenv import load_dotenv
from pandasai_litellm.litellm import LiteLLM
from function import sheets, load_excel, load_supabase
from semantic_layer import create_dataset

load_dotenv()
st.set_page_config(page_title="ME07 | Chat com dados", layout="wide")
st.title("Chat com os dados da ME07")
st.caption("PandasAI 3 + camada semântica + Gemini API")

origin = st.radio("Origem", ["Planilha local", "Supabase"], horizontal=True)
try:
    if origin == "Planilha local":
        sheet = st.selectbox("Aba", sheets())
        data = load_excel(sheet)
    else:
        sheet = os.getenv("DB_TABLE", "me07")
        data = load_supabase()
except Exception as exc:
    st.error(f"Falha ao carregar dados: {exc}")
    st.stop()

st.write(f"**{len(data)} registros**, **{len(data.columns)} colunas**")
with st.expander("Visualizar dados e colunas"):
    st.dataframe(data.head(20), use_container_width=True)
    st.write(", ".join(data.columns))

key = os.getenv("GEMINI_API_KEY")
if not key or key == "cole_sua_chave_aqui":
    st.warning("Configure GEMINI_API_KEY no arquivo .env.")
    st.stop()

with st.form("pergunta"):
    question = st.text_input("Pergunte aos dados")
    run = st.form_submit_button("Executar")
if run:
    if not question.strip():
        st.info("Digite uma pergunta.")
        st.stop()
    with st.spinner("Consultando a API e analisando a base..."):
        try:
            pai.config.set({"llm": LiteLLM(
                model=os.getenv("GEMINI_MODEL", "gemini/gemini-2.5-flash-lite"), api_key=key
            )})
            dataset, columns = create_dataset(data, sheet)
            response = dataset.chat(question.strip())
        except Exception as exc:
            st.error(f"Falha na análise: {exc}")
            st.stop()
    with st.expander("Camada semântica aplicada"):
        st.dataframe(pd.DataFrame(columns), use_container_width=True)
    code = getattr(response, "last_code_executed", None)
    if code:
        with st.expander("Código gerado"):
            st.code(str(code))
    kind = getattr(response, "type", None)
    value = getattr(response, "value", response)
    if kind == "number":
        st.metric("Resultado", value)
    elif kind == "dataframe" or isinstance(value, pd.DataFrame):
        st.dataframe(value, use_container_width=True)
    elif kind == "chart":
        st.image(str(value) if isinstance(value, Path) else value)
    elif kind == "error":
        st.error(str(value))
    else:
        st.write(value)
    st.caption("Confira a lógica e os resultados produzidos pela IA.")
