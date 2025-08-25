import streamlit as st
import pandas as pd
from datetime import datetime
import calendar
from utils.functions.general_functions import *
from utils.functions.conciliacoes import *
from utils.functions.farol_conciliacao import *
from utils.queries import *


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
    meses = ['Todos os meses', '1º Trimestre', '2º Trimestre', '3º Trimestre', '4º Trimestre', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    mes_farol = st.selectbox("Selecione um mês ou trimestre:", meses)

# Seletor de ano
with col2:
    ano_atual = datetime.now().year 
    anos = list(range(2024, ano_atual+1))
    index_padrao = anos.index(ano_atual)
    ano_farol = st.selectbox("Selecione um ano:", anos, index=index_padrao)

# Seletor de trimestre
# trimestres = ['1º Trimestre', '2º Trimestre', '3º Trimestre', '4º Trimestre']
# trimestre_farol = st.selectbox("Selecione um trimestre:", trimestres)

st.divider()

# Conciliação completa (2024 -- atual)
today = datetime.now()
last_year = today.year - 1
jan_last_year = datetime(last_year, 1, 1)
dec_this_year = datetime(today.year, 12, 31)
mes_atual = datetime.now().month
ano_atual = datetime.now().year

datas_completas = pd.date_range(start=jan_last_year, end=dec_this_year)
df_conciliacao_farol = pd.DataFrame()
df_conciliacao_farol['Data'] = datas_completas

# Calcula tabela de conciliação (2024 -- atual) de cada casa
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

# Calcula quantidade de dias em casa mês
for i in range(1, 13):
    dias_no_mes = calendar.monthrange(ano_farol, i)[1]
    qtd_dias.append(dias_no_mes)

df_meses = pd.DataFrame({'Mes': meses, 'Qtd_dias': qtd_dias})

conditions = [
    df_meses['Mes'].between(1, 3),
    df_meses['Mes'].between(4, 6),
    df_meses['Mes'].between(7, 9),
    df_meses['Mes'].between(10, 12)
]

# Calcula quantidade de dias em cada trimestre
choices = [1, 2, 3, 4]
df_trimestres = pd.DataFrame({'Mes': meses, 'Trimestre': np.select(conditions, choices, default=np.nan)})
df_trimestres = df_trimestres.merge(df_meses, right_on='Mes', left_on='Mes', how='inner')
df_dias_trimestre = df_trimestres.groupby(['Trimestre'])['Qtd_dias'].sum().reset_index()
df_trimestres = df_trimestres.merge(df_dias_trimestre, right_on='Trimestre', left_on='Trimestre', how='inner')

# Porcentagem de dias não conciliados por mês de cada casa
lista_conciliacao_arcos = lista_dias_nao_conciliados_casa(df_conciliacao_arcos, ano_farol, df_meses, mes_atual)
lista_conciliacao_b_centro = lista_dias_nao_conciliados_casa(df_conciliacao_b_centro, ano_farol, df_meses, mes_atual)
lista_conciliacao_b_granja = lista_dias_nao_conciliados_casa(df_conciliacao_b_granja, ano_farol, df_meses, mes_atual)
lista_conciliacao_b_paulista = lista_dias_nao_conciliados_casa(df_conciliacao_b_paulista, ano_farol, df_meses, mes_atual)
lista_conciliacao_leo_centro = lista_dias_nao_conciliados_casa(df_conciliacao_leo_centro, ano_farol, df_meses, mes_atual)
lista_conciliacao_leo_vila = lista_dias_nao_conciliados_casa(df_conciliacao_leo_vila, ano_farol, df_meses, mes_atual)
lista_conciliacao_blue_note = lista_dias_nao_conciliados_casa(df_conciliacao_blue_note, ano_farol, df_meses, mes_atual)
lista_conciliacao_blue_note_novo = lista_dias_nao_conciliados_casa(df_conciliacao_blue_note_novo, ano_farol, df_meses, mes_atual)
lista_conciliacao_rolim = lista_dias_nao_conciliados_casa(df_conciliacao_rolim, ano_farol, df_meses, mes_atual)
lista_conciliacao_fb = lista_dias_nao_conciliados_casa(df_conciliacao_fb, ano_farol, df_meses, mes_atual)
lista_conciliacao_girondino = lista_dias_nao_conciliados_casa(df_conciliacao_girondino, ano_farol, df_meses, mes_atual)
lista_conciliacao_girondino_ccbb = lista_dias_nao_conciliados_casa(df_conciliacao_girondino_ccbb, ano_farol, df_meses, mes_atual)
lista_conciliacao_jacare = lista_dias_nao_conciliados_casa(df_conciliacao_jacare, ano_farol, df_meses, mes_atual)
lista_conciliacao_love = lista_dias_nao_conciliados_casa(df_conciliacao_love, ano_farol, df_meses, mes_atual)
lista_conciliacao_orfeu = lista_dias_nao_conciliados_casa(df_conciliacao_orfeu, ano_farol, df_meses, mes_atual)
lista_conciliacao_priceless = lista_dias_nao_conciliados_casa(df_conciliacao_priceless, ano_farol, df_meses, mes_atual)
lista_conciliacao_riviera = lista_dias_nao_conciliados_casa(df_conciliacao_riviera, ano_farol, df_meses, mes_atual)
lista_conciliacao_sanduiche = lista_dias_nao_conciliados_casa(df_conciliacao_sanduiche, ano_farol, df_meses, mes_atual)
lista_conciliacao_tempus = lista_dias_nao_conciliados_casa(df_conciliacao_tempus, ano_farol, df_meses, mes_atual)
lista_conciliacao_ultra = lista_dias_nao_conciliados_casa(df_conciliacao_ultra, ano_farol, df_meses, mes_atual)

lista_casas_mes = [
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

# Porcentagem de dias não conciliados por trimestre de cada casa
lista_conciliacao_arcos_trim = lista_dias_nao_conciliados_casa_trim(df_conciliacao_arcos, ano_farol, df_trimestres, mes_farol)
lista_conciliacao_b_centro_trim = lista_dias_nao_conciliados_casa_trim(df_conciliacao_b_centro, ano_farol, df_trimestres, mes_farol)
lista_conciliacao_b_granja_trim = lista_dias_nao_conciliados_casa_trim(df_conciliacao_b_granja, ano_farol, df_trimestres, mes_farol)
lista_conciliacao_b_paulista_trim = lista_dias_nao_conciliados_casa_trim(df_conciliacao_b_paulista, ano_farol, df_trimestres, mes_farol)
lista_conciliacao_leo_centro_trim = lista_dias_nao_conciliados_casa_trim(df_conciliacao_leo_centro, ano_farol, df_trimestres, mes_farol)
lista_conciliacao_leo_vila_trim = lista_dias_nao_conciliados_casa_trim(df_conciliacao_leo_vila, ano_farol, df_trimestres, mes_farol)
lista_conciliacao_blue_note_trim = lista_dias_nao_conciliados_casa_trim(df_conciliacao_blue_note, ano_farol, df_trimestres, mes_farol)
lista_conciliacao_blue_note_novo_trim = lista_dias_nao_conciliados_casa_trim(df_conciliacao_blue_note_novo, ano_farol, df_trimestres, mes_farol)
lista_conciliacao_rolim_trim = lista_dias_nao_conciliados_casa_trim(df_conciliacao_rolim, ano_farol, df_trimestres, mes_farol)
lista_conciliacao_fb_trim = lista_dias_nao_conciliados_casa_trim(df_conciliacao_fb, ano_farol, df_trimestres, mes_farol)
lista_conciliacao_girondino_trim = lista_dias_nao_conciliados_casa_trim(df_conciliacao_girondino, ano_farol, df_trimestres, mes_farol)
lista_conciliacao_girondino_ccbb_trim = lista_dias_nao_conciliados_casa_trim(df_conciliacao_girondino_ccbb, ano_farol, df_trimestres, mes_farol)
lista_conciliacao_jacare_trim = lista_dias_nao_conciliados_casa_trim(df_conciliacao_jacare, ano_farol, df_trimestres, mes_farol)
lista_conciliacao_love_trim = lista_dias_nao_conciliados_casa_trim(df_conciliacao_love, ano_farol, df_trimestres, mes_farol)
lista_conciliacao_orfeu_trim = lista_dias_nao_conciliados_casa_trim(df_conciliacao_orfeu, ano_farol, df_trimestres, mes_farol)
lista_conciliacao_priceless_trim = lista_dias_nao_conciliados_casa_trim(df_conciliacao_priceless, ano_farol, df_trimestres, mes_farol)
lista_conciliacao_riviera_trim = lista_dias_nao_conciliados_casa_trim(df_conciliacao_riviera, ano_farol, df_trimestres, mes_farol)
lista_conciliacao_sanduiche_trim = lista_dias_nao_conciliados_casa_trim(df_conciliacao_sanduiche, ano_farol, df_trimestres, mes_farol)
lista_conciliacao_tempus_trim = lista_dias_nao_conciliados_casa_trim(df_conciliacao_tempus, ano_farol, df_trimestres, mes_farol)
lista_conciliacao_ultra_trim = lista_dias_nao_conciliados_casa_trim(df_conciliacao_ultra, ano_farol, df_trimestres, mes_farol)

lista_casas_trim = [
    lista_conciliacao_arcos_trim,
    lista_conciliacao_b_centro_trim,
    lista_conciliacao_b_granja_trim,
    lista_conciliacao_b_paulista_trim,
    lista_conciliacao_leo_centro_trim,
    lista_conciliacao_leo_vila_trim,
    lista_conciliacao_blue_note_trim,
    lista_conciliacao_blue_note_novo_trim,
    lista_conciliacao_rolim_trim,
    lista_conciliacao_fb_trim,
    lista_conciliacao_girondino_trim,
    lista_conciliacao_girondino_ccbb_trim,
    lista_conciliacao_jacare_trim,
    lista_conciliacao_love_trim,
    lista_conciliacao_orfeu_trim,
    lista_conciliacao_priceless_trim,
    lista_conciliacao_riviera_trim,
    lista_conciliacao_sanduiche_trim,
    lista_conciliacao_tempus_trim,
    lista_conciliacao_ultra_trim
]

# Exibe gráficos
with st.container(border=True):
    col1, col2, col3 = st.columns([0.1, 3, 0.1], vertical_alignment="center")
    with col2:
        st.subheader(f"% Dias não conciliados - {mes_farol}")
        if mes_farol == 'Todos os meses':
            grafico_dias_nao_conciliados(casas_validas, nomes_meses, lista_casas_mes)  
        elif mes_farol == '1º Trimestre' or mes_farol == '2º Trimestre' or mes_farol == '3º Trimestre' or mes_farol == '4º Trimestre':
            grafico_dias_nao_conciliados_trim(casas_validas, mes_farol, lista_casas_trim)
        else:   
            grafico_dias_nao_conciliados_mes(casas_validas, lista_casas_mes, mes_farol, df_conciliacao_farol, ano_farol, datas_completas)



