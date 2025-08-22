import streamlit as st
import pandas as pd
from datetime import datetime
import calendar
from utils.functions.general_functions import *
from utils.functions.conciliacoes import *
from utils.functions.farol_conciliacao import *
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

# Seletor de mês
with col1: 
    meses = ['Todos os meses', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    mes_farol = st.selectbox("Selecione um mês:", meses)

# Seletor de ano
with col2:
    ano_atual = datetime.now().year 
    anos = list(range(2024, ano_atual+1))
    index_padrao = anos.index(ano_atual)
    ano_farol = st.selectbox("Selecione um ano:", anos, index=index_padrao)

st.divider()

# Conciliação completa (2024 -- atual)
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

lista_casas = [
    lista_conciliacao_arcos,
    lista_conciliacao_b_centro,
    lista_conciliacao_b_granja,
    lista_conciliacao_b_paulista,
    lista_conciliacao_leo_centro,
    lista_conciliacao_leo_vila,
    lista_conciliacao_blue_note,
    lista_conciliacao_blue_note_novo,
    lista_conciliacao_rolim,
    lista_conciliacao_fb,
    lista_conciliacao_girondino,
    lista_conciliacao_girondino_ccbb,
    lista_conciliacao_jacare,
    lista_conciliacao_love,
    lista_conciliacao_orfeu,
    lista_conciliacao_priceless,
    lista_conciliacao_riviera,
    lista_conciliacao_sanduiche,
    lista_conciliacao_tempus,
    lista_conciliacao_ultra
]

# Exibe gráficos
with st.container(border=True):
    st.subheader("% Dias não conciliados por casa e mês")
    grafico_dias_nao_conciliados(casas_validas, nomes_meses, lista_casas)    
    
st.divider()

