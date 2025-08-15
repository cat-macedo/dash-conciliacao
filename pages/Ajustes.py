import streamlit as st
import pandas as pd
from utils.functions.general_functions import *
from utils.queries import *
from streamlit_echarts import st_echarts
from datetime import datetime
from decimal import Decimal


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

st.title(":moneybag: Ajustes")
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
        casa = "All bar"

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

# Filtra tabela de ajustes por casa e ano
df_ajustes = st.session_state["df_ajustes_conciliacao"]
if id_casa != 157:
    df_ajustes_filtrado = df_ajustes[df_ajustes["ID_Casa"] == id_casa]
    df_ajustes_filtrado = df_ajustes_filtrado[df_ajustes_filtrado['Data_Ajuste'].dt.year == ano]
else: 
    df_ajustes_filtrado = df_ajustes[df_ajustes['Data_Ajuste'].dt.year == ano]

# Pega o mês da data do ajuste
df_ajustes_filtrado_copia = df_ajustes_filtrado.copy()
df_ajustes_filtrado_copia['Mes'] = df_ajustes_filtrado_copia['Data_Ajuste'].dt.month

# Contabiliza ajustes por mês
nomes_meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
df_meses = pd.DataFrame({'Mes': list(range(1, 13)), 'Nome_Mes': nomes_meses})
df_ajustes_filtrado_copia = df_ajustes_filtrado_copia.merge(df_meses, on='Mes', how='right')

ajustes_mes = df_ajustes_filtrado_copia.groupby(['Mes'])['Casa'].count().reset_index()
ajustes_mes.rename(columns = {'Casa':'Qtd_Ajustes'}, inplace=True)
lista_ajustes_mes = ajustes_mes['Qtd_Ajustes'].tolist()

total_ajustes_mes = df_ajustes_filtrado_copia.groupby(['Mes'])['Valor'].sum().reset_index()
lista_total_ajustes_mes = total_ajustes_mes['Valor'].tolist()
lista_total_ajustes_mes = [float(valor) if isinstance(valor, Decimal) else valor for valor in lista_total_ajustes_mes]


# Não ficou bom
# option = {
#   "tooltip": {
#     "trigger": 'axis',
#     "axisPointer": {
#       "type": 'shadow'
#     }
#   },
#   "legend": {
#     "data": ['Quantidade de Ajustes', 'Total de Ajustes']
#   },
#   "xAxis": [
#     {
#       "type": 'category',
#       "axisTick": { "show": False },
#       "data": nomes_meses
#     }
#   ],
#   "yAxis": [
#     {
#       "type": 'value'
#     }
#   ],
#   "series": [
#     {
#       "name": 'Quantidade de Ajustes',
#       "type": 'bar',
#       "barGap": 0,
#       "emphasis": {
#         "focus": 'series'
#       },
#       "data": lista_ajustes_mes
#     },
#     {
#       "name": 'Total de Ajustes',
#       "type": 'bar',
#       "emphasis": {
#         "focus": 'series'
#       },
#       "data": lista_total_ajustes_mes
#     }
#   ]
# }

# Gráfico: total de ajustes por mês
grafico_total_ajustes = {
    "title": {
      "text": "Valor total de ajustes por mês"
    },
    "tooltip": {
      "trigger": "axis",
      "axisPointer": {
        "type": "shadow"
      }
    },
    "grid": {
      "top": 80,
      "bottom": 30
    },
    "xAxis": {
      "type": "value",
      "position": "top",
      "splitLine": {
        "lineStyle": {
          "type": "dashed"
        }
      }
    },
    "yAxis": {
      "type": "category",
      "axisLine": { "show": False },
      "axisLabel": { "show": False },
      "axisTick": { "show": False },
      "splitLine": { "show": False },
      "data": nomes_meses
    },
    "series": [
      {
        "name": "Total de Ajustes",
        "type": "bar",
        "stack": "Total",
        "label": {
          "show": True,
          "formatter": "{b}",
          "position": "left"
        },
        "data": lista_total_ajustes_mes
      }
    ]
  }

# Gráfico: quantidade de ajustes por mês
grafico_qtd_ajustes = {
    "title": {
      "text": "Quantidade de ajustes por mês"
    },
  "tooltip": {
    "trigger": 'axis',
    "axisPointer": {
      "type": 'shadow'
    }
  },
#   "legend": {
#     "data": ['Quantidade de Ajustes', 'Total de Ajustes']
#   },
  "xAxis": [
    {
      "type": 'category',
      "axisTick": { "show": False },
      "data": nomes_meses
    }
  ],
  "yAxis": [
    {
      "type": 'value'
    }
  ],
  "series": [
    {
      "name": 'Quantidade de Ajustes',
      "type": 'bar',
      "barGap": 0,
      "emphasis": {
        "focus": 'series'
      },
      "data": lista_ajustes_mes
    }
  ]
}

events = {
    "click": "function(params) { return params.name; }"
}

with st.container(border=True):
    teste = st_echarts(options=grafico_total_ajustes, events=events, height="320px", width="100%")
    st.write(teste)

with st.container(border=True):
    st_echarts(options=grafico_qtd_ajustes, height="320px", width="100%")
