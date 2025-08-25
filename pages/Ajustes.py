import streamlit as st
import pandas as pd
from utils.functions.general_functions import *
from utils.functions.ajustes import *
from utils.queries import *
from streamlit_echarts import st_echarts
from datetime import datetime
# from decimal import Decimal


st.set_page_config(
    page_title="Conciliação FB - Ajustes",
    page_icon=":moneybag:",
    layout="wide"
)

# Se der refresh, volta para página de login
if 'loggedIn' not in st.session_state or not st.session_state['loggedIn']:
	st.switch_page('Main.py')

# Personaliza menu lateral
config_sidebar()

st.title("⚖️ Ajustes")
st.divider()


# Filtrando por casa e ano
col1, col2 = st.columns(2)

# Seletor de casa
with col1: 
  df_casas = st.session_state["df_casas"]
  casas = df_casas['Casa'].tolist()

  casas = ["Todas as casas" if c == "All bar" else c for c in casas]
  casa = st.selectbox("Selecione uma casa:", casas)
  if casa == "Todas as casas":
    nome_casa = "Todas as casas"
    casa = "All bar"
  else:
     nome_casa = casa

  # Definindo um dicionário para mapear nomes de casas a IDs de casas
  mapeamento_casas = dict(zip(df_casas["Casa"], df_casas["ID_Casa"]))

  # Obtendo o ID da casa selecionada
  id_casa = mapeamento_casas[casa]

# Seletor de ano
with col2:
  ano_atual = datetime.now().year 
  anos = list(range(2024, ano_atual+1))
  index_padrao = anos.index(ano_atual)
  ano = st.selectbox("Selecione um ano:", anos, index=index_padrao)

st.divider()

# Define df usados nos gráficos
df_ajustes_filtrado = define_df_ajustes(id_casa, ano)
lista_total_ajustes_mes_fmt = total_ajustes_mes(df_ajustes_filtrado)
lista_qtd_ajustes_mes = qtd_ajustes_mes(df_ajustes_filtrado)


with st.container(border=True):
  if len(lista_total_ajustes_mes_fmt) == 0 and all(v == 0 for v in lista_qtd_ajustes_mes):
    st.warning("Não há ajustes a serem exibidos")
  else: 
    col1, col2, col3 = st.columns([0.1, 3, 0.1], vertical_alignment="center")
    with col2:
      # Exibe primeiro gráfico
      st.subheader(f"Valor total de ajustes por mês - {nome_casa}")
      grafico_total_ajustes(df_ajustes_filtrado, lista_total_ajustes_mes_fmt)
      st.divider()

      # Exibe segundo gráfico
      st.subheader(f"Quantidade de ajustes por mês - {nome_casa}")
      grafico_ajustes_mes(df_ajustes_filtrado, lista_qtd_ajustes_mes)
  

df_total_ajustes_arcos, df_qtd_ajustes_arcos = df_ajustes_casa("Arcos", ano)
st.write(df_total_ajustes_arcos, df_qtd_ajustes_arcos)

	