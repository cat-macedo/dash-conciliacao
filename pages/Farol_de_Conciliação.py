import streamlit as st
import pandas as pd
from datetime import datetime
import calendar
from utils.functions.general_functions import *
from utils.functions.conciliacoes import *
from utils.queries import *
from workalendar.america import Brazil


st.set_page_config(
    page_title="Conciliação FB - Farol",
    page_icon=":moneybag:",
    layout="wide"
)

# Se der refresh, volta para página de login
if 'loggedIn' not in st.session_state or not st.session_state['loggedIn']:
	st.switch_page('Main.py')

# Personaliza menu lateral
config_sidebar()

st.title("🚦 Farol de conciliação")
st.divider()


# Filtrando por casa e ano
col1, col2 = st.columns(2)

# Seletor de casa
# with col1: 
#     df_casas = st.session_state["df_casas"]
#     casas = df_casas['Casa'].tolist()

#     casas = ["Todas as casas" if c == "All bar" else c for c in casas]
#     casa_farol = st.selectbox("Selecione uma casa:", casas)
#     if casa_farol == "Todas as casas":
#         casa_farol = "All bar"

# # Definindo um dicionário para mapear nomes de casas a IDs de casas
# mapeamento_casas = dict(zip(df_casas["Casa"], df_casas["ID_Casa"]))

# # Obtendo o ID da casa selecionada
# id_casa_farol = mapeamento_casas[casa_farol]

# Seletor de ano
with col2:
    ano_atual = datetime.now().year 
    anos = list(range(2024, ano_atual+1))
    index_padrao = anos.index(ano_atual)
    ano_farol = st.selectbox("Selecione um ano:", anos, index=index_padrao)

st.divider()

# Conciliação completa (2024 a 2025)
today = datetime.now()
last_year = today.year - 1
jan_last_year = datetime(last_year, 1, 1)
dec_this_year = datetime(today.year, 12, 31)
mes_atual = datetime.now().month

datas_completas = pd.date_range(start=jan_last_year, end=dec_this_year)
df_conciliacao_farol = pd.DataFrame()
df_conciliacao_farol['Data'] = datas_completas

df_conciliacao_arcos = conciliacao_casa(df_conciliacao_farol, "Arcos", datas_completas)
df_conciliacao_b_centro = conciliacao_casa(df_conciliacao_farol, "Bar Brahma - Centro", datas_completas)
df_conciliacao_b_granja = conciliacao_casa(df_conciliacao_farol, "Bar Brahma - Granja", datas_completas)
df_conciliacao_b_paulista = conciliacao_casa(df_conciliacao_farol, "Bar Brahma Paulista", datas_completas)
df_conciliacao_leo_centro = conciliacao_casa(df_conciliacao_farol, "Bar Léo - Centro", datas_completas)
df_conciliacao_leo_vila = conciliacao_casa(df_conciliacao_farol, "Bar Léo - Vila Madalena", datas_completas)
df_conciliacao_blue_note = conciliacao_casa(df_conciliacao_farol, "Blue Note - São Paulo", datas_completas)
df_conciliacao_blue_note_novo = conciliacao_casa(df_conciliacao_farol, "Blue Note SP (Novo)", datas_completas)
df_conciliacao_rolim = conciliacao_casa(df_conciliacao_farol, "Edificio Rolim", datas_completas)
df_conciliacao_fb = conciliacao_casa(df_conciliacao_farol, "Escritório Fabrica de Bares", datas_completas)
df_conciliacao_girondino = conciliacao_casa(df_conciliacao_farol, "Girondino ", datas_completas)
df_conciliacao_girondino_ccbb = conciliacao_casa(df_conciliacao_farol, "Girondino - CCBB", datas_completas)
df_conciliacao_jacare = conciliacao_casa(df_conciliacao_farol, "Jacaré", datas_completas)
df_conciliacao_love = conciliacao_casa(df_conciliacao_farol, "Love Cabaret", datas_completas)
df_conciliacao_orfeu = conciliacao_casa(df_conciliacao_farol, "Orfeu", datas_completas)
df_conciliacao_priceless = conciliacao_casa(df_conciliacao_farol, "Priceless", datas_completas)
df_conciliacao_riviera = conciliacao_casa(df_conciliacao_farol, "Riviera Bar", datas_completas)
df_conciliacao_sanduiche = conciliacao_casa(df_conciliacao_farol, "Sanduiche comunicação LTDA ", datas_completas)
df_conciliacao_tempus = conciliacao_casa(df_conciliacao_farol, "Tempus Fugit  Ltda ", datas_completas)
df_conciliacao_ultra = conciliacao_casa(df_conciliacao_farol, "Ultra Evil Premium Ltda ", datas_completas)

casas_validas = ['Arcos', 'Bar Brahma - Centro', 'Bar Brahma - Granja', 'Bar Brahma Paulista', 'Bar Léo - Centro', 'Bar Léo - Vila Madalena', 'Blue Note - São Paulo', 'Blue Note SP (Novo)', 'Edificio Rolim', 'Escritório Fabrica de Bares', 'Girondino', 'Girondino - CCBB', 'Jacaré', 'Love Cabaret', 'Orfeu', 'Priceless', 'Riviera Bar', 'Sanduiche comunicação LTDA', 'Tempus Fugit  Ltda', 'Ultra Evil Premium Ltda']
nomes_meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
meses = list(range(1, 13))
qtd_dias = []

for i in range(1, 13):
    dias_no_mes = calendar.monthrange(ano_farol, i)[1]
    qtd_dias.append(dias_no_mes)

df_meses = pd.DataFrame({'Mes': meses, 'Qtd_dias': qtd_dias})

# Falta outras casas
lista_conciliacao_arcos = dias_nao_conciliados_casa(df_conciliacao_arcos, ano_farol, df_meses, mes_atual)
lista_conciliacao_b_centro = dias_nao_conciliados_casa(df_conciliacao_b_centro, ano_farol, df_meses, mes_atual)
lista_conciliacao_b_granja = dias_nao_conciliados_casa(df_conciliacao_b_granja, ano_farol, df_meses, mes_atual)
lista_conciliacao_b_paulista = dias_nao_conciliados_casa(df_conciliacao_b_paulista, ano_farol, df_meses, mes_atual)
lista_conciliacao_leo_centro = dias_nao_conciliados_casa(df_conciliacao_leo_centro, ano_farol, df_meses, mes_atual)
lista_conciliacao_leo_vila = dias_nao_conciliados_casa(df_conciliacao_leo_vila, ano_farol, df_meses, mes_atual)
lista_conciliacao_blue_note = dias_nao_conciliados_casa(df_conciliacao_blue_note, ano_farol, df_meses, mes_atual)
lista_conciliacao_blue_note_novo = dias_nao_conciliados_casa(df_conciliacao_blue_note_novo, ano_farol, df_meses, mes_atual)
lista_conciliacao_rolim = dias_nao_conciliados_casa(df_conciliacao_rolim, ano_farol, df_meses, mes_atual)
lista_conciliacao_fb = dias_nao_conciliados_casa(df_conciliacao_fb, ano_farol, df_meses, mes_atual)
lista_conciliacao_girondino = dias_nao_conciliados_casa(df_conciliacao_girondino, ano_farol, df_meses, mes_atual)
lista_conciliacao_girondino_ccbb = dias_nao_conciliados_casa(df_conciliacao_girondino_ccbb, ano_farol, df_meses, mes_atual)
lista_conciliacao_jacare = dias_nao_conciliados_casa(df_conciliacao_jacare, ano_farol, df_meses, mes_atual)
lista_conciliacao_love = dias_nao_conciliados_casa(df_conciliacao_love, ano_farol, df_meses, mes_atual)
lista_conciliacao_orfeu = dias_nao_conciliados_casa(df_conciliacao_orfeu, ano_farol, df_meses, mes_atual)
lista_conciliacao_priceless = dias_nao_conciliados_casa(df_conciliacao_priceless, ano_farol, df_meses, mes_atual)
lista_conciliacao_riviera = dias_nao_conciliados_casa(df_conciliacao_riviera, ano_farol, df_meses, mes_atual)
lista_conciliacao_sanduiche = dias_nao_conciliados_casa(df_conciliacao_sanduiche, ano_farol, df_meses, mes_atual)
lista_conciliacao_tempus = dias_nao_conciliados_casa(df_conciliacao_tempus, ano_farol, df_meses, mes_atual)
lista_conciliacao_ultra = dias_nao_conciliados_casa(df_conciliacao_ultra, ano_farol, df_meses, mes_atual)


grafico_dias_conciliados = {
    # "title": {
    #   "text": "Valor total de ajustes por mês"   
    # },
    "tooltip": {
        "trigger": 'axis',
        "axisPointer": {
        "type": 'shadow'
        }
    },
    "legend": {
    "data": casas_validas,
    "type": "scroll", 
    "bottom": 0
    },
    "grid": {
        "left": "4%",
        "right": "4%",
        "bottom": "10%",
        # "top": "10%",
        "containLabel": True
    },
    "xAxis": [
        {
        "type": 'category',
        "axisTick": { "show": True },
        "data": nomes_meses
        }
    ],
    "yAxis": [
        {
        "type": 'value',
        "min": 0,
        "max": 100,
        "interval": 20,
        "axisLabel": {
        "formatter": '{value} %'
        }
        } 
    ],
    "series": [
        {
        "name": 'Arcos',
        "type": 'bar',
        # "barWidth": "50%",
        "barGap": "10%",
        "data": lista_conciliacao_arcos,
        # "label": {
        #     "show": True,
        #     "position": "top",
        # }
        },
        {
        "name": 'Bar Brahma - Centro',
        "type": 'bar',
        # "barWidth": "50%",
        "barGap": "10%",
        "data": lista_conciliacao_b_centro,
        # "label": {
        #     "show": True,
        #     "position": "top",
        # }
        },
        {
        "name": 'Bar Brahma - Granja',
        "type": 'bar',
        # "barWidth": "50%",
        "barGap": "10%",
        "data": lista_conciliacao_b_granja,
        # "label": {
        #     "show": True,
        #     "position": "top",
        # }
        },
        {
        "name": 'Bar Brahma Paulista',
        "type": 'bar',
        # "barWidth": "50%",
        "barGap": "10%",
        "data": lista_conciliacao_b_paulista,
        # "label": {
        #     "show": True,
        #     "position": "top",
        # }
        },
        {
        "name": 'Bar Léo - Centro',
        "type": 'bar',
        # "barWidth": "50%",
        "barGap": "10%",
        "data": lista_conciliacao_leo_centro,
        # "label": {
        #     "show": True,
        #     "position": "top",
        # }
        },
        {
        "name": 'Bar Léo - Vila Madalena',
        "type": 'bar',
        # "barWidth": "50%",
        "barGap": "10%",
        "data": lista_conciliacao_leo_vila,
        # "label": {
        #     "show": True,
        #     "position": "top",
        # }
        },
        {
        "name": 'Blue Note - São Paulo',
        "type": 'bar',
        # "barWidth": "50%",
        "barGap": "10%",
        "data": lista_conciliacao_blue_note,
        # "label": {
        #     "show": True,
        #     "position": "top",
        # }
        },
        {
        "name": 'Blue Note SP (Novo)',
        "type": 'bar',
        # "barWidth": "50%",
        "barGap": "10%",
        "data": lista_conciliacao_blue_note_novo,
        # "label": {
        #     "show": True,
        #     "position": "top",
        # }
        },
        {
        "name": 'Edificio Rolim',
        "type": 'bar',
        # "barWidth": "50%",
        "barGap": "10%",
        "data": lista_conciliacao_rolim,
        # "label": {
        #     "show": True,
        #     "position": "top",
        # }
        },
        {
        "name": 'Escritório Fabrica de Bares',
        "type": 'bar',
        # "barWidth": "50%",
        "barGap": "10%",
        "data": lista_conciliacao_fb,
        # "label": {
        #     "show": True,
        #     "position": "top",
        # }
        },
        {
        "name": 'Girondino',
        "type": 'bar',
        # "barWidth": "50%",
        "barGap": "10%",
        "data": lista_conciliacao_girondino,
        # "label": {
        #     "show": True,
        #     "position": "top",
        # }
        },
        {
        "name": 'Girondino - CCBB',
        "type": 'bar',
        # "barWidth": "50%",
        "barGap": "10%",
        "data": lista_conciliacao_girondino_ccbb,
        # "label": {
        #     "show": True,
        #     "position": "top",
        # }
        },
        {
        "name": 'Jacaré',
        "type": 'bar',
        # "barWidth": "50%",
        "barGap": "10%",
        "data": lista_conciliacao_jacare,
        # "label": {
        #     "show": True,
        #     "position": "top",
        # }
        },
        {
        "name": 'Love Cabaret',
        "type": 'bar',
        # "barWidth": "50%",
        "barGap": "10%",
        "data": lista_conciliacao_love,
        # "label": {
        #     "show": True,
        #     "position": "top",
        # }
        },
        {
        "name": 'Orfeu',
        "type": 'bar',
        # "barWidth": "50%",
        "barGap": "10%",
        "data": lista_conciliacao_orfeu,
        # "label": {
        #     "show": True,
        #     "position": "top",
        # }
        },
        {
        "name": 'Priceless',
        "type": 'bar',
        # "barWidth": "50%",
        "barGap": "10%",
        "data": lista_conciliacao_priceless,
        # "label": {
        #     "show": True,
        #     "position": "top",
        # }
        },
        {
        "name": 'Riviera Bar',
        "type": 'bar',
        # "barWidth": "50%",
        "barGap": "10%",
        "data": lista_conciliacao_riviera,
        # "label": {
        #     "show": True,
        #     "position": "top",
        # }
        },
        {
        "name": 'Sanduiche comunicação LTDA',
        "type": 'bar',
        # "barWidth": "50%",
        "barGap": "10%",
        "data": lista_conciliacao_sanduiche,
        # "label": {
        #     "show": True,
        #     "position": "top",
        # }
        },
        {
        "name": 'Tempus Fugit  Ltda',
        "type": 'bar',
        # "barWidth": "50%",
        "barGap": "10%",
        "data": lista_conciliacao_tempus,
        # "label": {
        #     "show": True,
        #     "position": "top",
        # }
        },
        {
        "name": 'Ultra Evil Premium Ltda',
        "type": 'bar',
        # "barWidth": "50%",
        "barGap": "10%",
        "data": lista_conciliacao_ultra,
        # "label": {
        #     "show": True,
        #     "position": "top",
        # }
        },   
              
    ]
}

with st.container(border=True):
    st.subheader("% Dias conciliados por casa e mês")
    st_echarts(options=grafico_dias_conciliados, height="600px", width="100%")

st.divider()

