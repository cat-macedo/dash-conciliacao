import streamlit as st
import pandas as pd
from datetime import datetime
from utils.functions.general_functions import *
from utils.functions.conciliacoes import *
from utils.functions.farol_conciliacao import *
from utils.queries import *

ano_atual = datetime.now().year

cores_casas = [
    "#582310", "#DF2526", "#84161f", "#1C6EBA", "#E9A700", "#FF8800", "#081F5C", "#004080",
    "#336699", "#6699CC", "#4A5129", "#8CA706", "#0CA22E", "#E799BB", "#006E77", "#000000",
    "#C2185B", "#FF6600", "#9933CC", "#330099"
    ]


# Calcula porcentagem de dias não conciliados por mês de cada casa
def lista_dias_nao_conciliados_casa(df_casa, ano_farol, df_meses, mes_atual):
    df_dias_nao_conciliados = df_casa[df_casa['Data'].dt.year == ano_farol]
    df_dias_nao_conciliados = df_dias_nao_conciliados[df_dias_nao_conciliados['Conciliação'] != 0.0]
    df_dias_nao_conciliados['Data'] = df_dias_nao_conciliados['Data'].dt.month # Mês dos dias não conciliados

    # Contagem de dias não conciliados por mês
    df_qtd_dias_nao_conciliados_mes = df_dias_nao_conciliados.groupby(['Data'])['Conciliação'].count().reset_index()
    df_qtd_dias_nao_conciliados_mes = df_qtd_dias_nao_conciliados_mes.merge(df_meses, left_on='Data', right_on='Mes', how='right')

    # Porcentagem de dias não conciliados por mês -> qtd dias não conciliados / total de dias no mês
    df_qtd_dias_nao_conciliados_mes['Porcentagem'] = df_qtd_dias_nao_conciliados_mes['Conciliação'] / df_qtd_dias_nao_conciliados_mes['Qtd_dias']
    df_qtd_dias_nao_conciliados_mes['Porcentagem'] = df_qtd_dias_nao_conciliados_mes['Porcentagem'].fillna(0) # Preenche meses None com zero (tem todos os dias conciliados ou meses depois do atual)

    # Lista com meses (0-11) e a porcentagem de dias não conciliados
    porc_dias_nao_conciliados = df_qtd_dias_nao_conciliados_mes['Porcentagem'].tolist()

    lista_dias_nao_conciliados = []
    for i, dia in enumerate(porc_dias_nao_conciliados):
        if (i <= mes_atual - 1) and (ano_farol == ano_atual):
            dia = dia * 100  # 2 casas decimais
        elif (i > mes_atual - 1) and (ano_farol == ano_atual):
            dia = 0 # meses depois do atual: 0 conciliação
        else:
            dia = dia * 100  # para anos anteriores, sempre multiplica
        dia = round(dia, 2)
        lista_dias_nao_conciliados.append(dia)

    #st.write(df_dias_nao_conciliados) # vou precisar
    # lista_dias_nao_conciliados = [v if v != 0 else None for v in lista_dias_nao_conciliados]  # None não é plotado
    return lista_dias_nao_conciliados


# Cria dataframe com dias não conciliados da casa clicada no mês específico
def dias_nao_conciliados_casa_mes(df_conciliacao_farol, casa_selecionada, mes_selecionado, ano_farol, datas_completas):
    # Gera tabela de conciliação da casa
    df_conciliacao_casa = conciliacao_casa(df_conciliacao_farol, casa_selecionada, datas_completas) 

    # Filtra por ano do farol e mês
    df_dias_nao_conciliados_casa = df_conciliacao_casa[
    (df_conciliacao_casa['Data'].dt.year == ano_farol) &
    (df_conciliacao_casa['Data'].dt.month == (mes_selecionado + 1))
    ]
    
    # Filtra por dias com conciliação != 0
    df_dias_nao_conciliados_casa = df_dias_nao_conciliados_casa[df_dias_nao_conciliados_casa['Conciliação'] != 0.0]
    qtd_dias_nao_conciliados = df_dias_nao_conciliados_casa['Conciliação'].count()
    return df_dias_nao_conciliados_casa, qtd_dias_nao_conciliados


# Gráfico com todos os meses e todas as casas (default)
def grafico_dias_nao_conciliados(casas_validas, nomes_meses, lista_casas):
    
    # Define as séries (barras) do eixo x (uma para cada casa)
    series = [
        {
            "name": nome,
            "type": "bar",
            "barGap": "10%",
            "data": lista_casas[i],
            "itemStyle": {"color": cores_casas[i]}
        }
        for i, nome in enumerate(casas_validas)
    ]

    grafico_dias_nao_conciliados = {
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "legend": {
            "data": casas_validas,
            "orient": "vertical",   # legenda em coluna
            "right": "0%",        
            "top": "center",
            "backgroundColor": "#ffffff55",
        },
        "grid": {
            "left": "2%", 
            "right": "23%", 
            "bottom": "0%", 
            "containLabel": True},
        "xAxis": [{
            "type": "category", 
            "axisTick": {"show": True}, 
            "data": nomes_meses}],
        "yAxis": [
            {
            "type": "value", 
            # "min": 0,
            # "max": 50,
            # "interval": 10,
            "axisLabel": {"formatter": "{value} %"}
            }
        ],
        "series": series
    }

    # Evento de clique - abre o mês
    # events = {
    #     "click": "function(params) { return params.name; }"
    # }
    
    # mes_selecionado = st_echarts(options=grafico_dias_nao_conciliados, events=events, height="600px", width="100%")
    st_echarts(options=grafico_dias_nao_conciliados, height="600px", width="100%")


# Gráfico exibido ao selecionar um mês 
def grafico_dias_nao_conciliados_mes(casas_validas, lista_casas, mes_selecionado, df_conciliacao_farol, ano_farol, datas_completas):
    for i, casa in enumerate(lista_casas):
        for j, valor in enumerate(casa):
            if valor is None:
                lista_casas[i][j] = 0

    nomes_meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    for mes in nomes_meses:
        if mes_selecionado == mes:
            nome_mes = mes
            mes_selecionado = nomes_meses.index(mes)

    lista_mes = []
    for casa in lista_casas:
        lista_mes.append(casa[mes_selecionado])
    
    # Define as séries (barras) do eixo x (uma para cada casa)
    series = [
        {
            "name": nome,
            "type": "bar",
            "barGap": "10%",
            "data": [lista_mes[i]],
            "backgroundStyle": {
                "color": 'rgba(180, 180, 180, 0.2)'
            },
            "itemStyle": {"color": cores_casas[i]},
            "label": {
                "show": True,
                "position": "top" 
            }
        }
        for i, nome in enumerate(casas_validas)
    ]

    grafico_dias_nao_conciliados_mes = {
        "tooltip": {
            "trigger": "axis", 
            "axisPointer": {"type": "shadow"}},
        "legend": {
            "data": casas_validas,
            "orient": "vertical",   # legenda em coluna
            "right": "0%",        
            "top": "center",
            "backgroundColor": "#ffffff55",
        },
        "grid": {
            "left": "2%", 
            "right": "23%", 
            "bottom": "0%", 
            "containLabel": True
        },
        "xAxis": {
            "type": 'category',
            "data": [nome_mes]
        },
        "yAxis": {
            "type": 'value',
            "axisLabel": {"formatter": "{value} %"}
        },
        "series": series
    }

    # Evento de clique - seleciona a casa
    events = {
        "click": "function(params) { return params.seriesName; }"
    }
    
    casa_selecionada = st_echarts(options=grafico_dias_nao_conciliados_mes, events=events, height="550px", width="100%")

    if not casa_selecionada:
        st.warning("Selecione uma casa para visualizar os dias não conciliados")
    else:
        # Exibe dataframe dos dias não conciliados da casa no mês
        st.divider()
        st.subheader(f"Dias não conciliados - {casa_selecionada}")
        df_dias_nao_conciliados_casa, qtd_dias_nao_conciliados = dias_nao_conciliados_casa_mes(df_conciliacao_farol, casa_selecionada, mes_selecionado, ano_farol, datas_completas)
        df_dias_nao_conciliados_casa_fmt = formata_df(df_dias_nao_conciliados_casa)
        st.dataframe(df_dias_nao_conciliados_casa_fmt, hide_index=True)
        st.write(f'**Quantidade de dias não conciliados:** {qtd_dias_nao_conciliados}')


# Cálculos por trimestre #
def lista_dias_nao_conciliados_casa_trim(df_casa, ano_farol, df_trimestres, trim_selecionado):
    df_dias_nao_conciliados = df_casa[df_casa['Data'].dt.year == ano_farol]
    df_dias_nao_conciliados = df_dias_nao_conciliados[df_dias_nao_conciliados['Conciliação'] != 0.0]
    df_dias_nao_conciliados['Mes'] = df_dias_nao_conciliados['Data'].dt.month # Mês dos dias não conciliados

    # Contagem de dias não conciliados por mês
    df_dias_nao_conciliados_trim = df_dias_nao_conciliados.merge(df_trimestres, left_on='Mes', right_on='Mes', how='right')
    
    # Porcentagem de dias não conciliados por trimestre
    df_qtd_dias_nao_conciliados_trim = df_dias_nao_conciliados_trim.groupby(['Trimestre'])['Conciliação'].count().reset_index()
    df_qtd_dias_nao_conciliados_trim = df_qtd_dias_nao_conciliados_trim.merge(df_trimestres, right_on='Trimestre', left_on='Trimestre', how='left')
    df_unico_por_trimestre = df_qtd_dias_nao_conciliados_trim.drop_duplicates(subset=['Trimestre'], keep='first').copy()
    df_unico_por_trimestre['Porcentagem'] = (df_unico_por_trimestre['Conciliação'] / df_unico_por_trimestre['Qtd_dias_y']) 
    
    porc_dias_nao_conciliados_trim = df_unico_por_trimestre['Porcentagem'].tolist()

    # Lista com trimestres (0-3) e a porcentagem de dias não conciliados 
    lista_dias_nao_conciliados_trim = []
    for i in porc_dias_nao_conciliados_trim:
        i = round((i*100), 2)
        lista_dias_nao_conciliados_trim.append(i)

    if trim_selecionado == '1º Trimestre':
        return lista_dias_nao_conciliados_trim[0] 
    elif trim_selecionado == '2º Trimestre':
        return lista_dias_nao_conciliados_trim[1]
    elif trim_selecionado == '3º Trimestre':
        return lista_dias_nao_conciliados_trim[2]
    elif trim_selecionado == '4º Trimestre':
        return lista_dias_nao_conciliados_trim[3]
    

# Cria tabela com dias não conciliados de cada casa por trimestre
def dias_nao_conciliados_casa_trim(df_conciliacao_farol, casa_selecionada, trim_selecionado, ano_farol, datas_completas):
    
    # Gera tabela de conciliação da casa
    df_conciliacao_casa = conciliacao_casa(df_conciliacao_farol, casa_selecionada, datas_completas) 

    # Filtra por ano do farol e trimestre
    if trim_selecionado == '1º Trimestre':
        df_dias_nao_conciliados_casa = df_conciliacao_casa[
        (df_conciliacao_casa['Data'].dt.year == ano_farol) &
        (df_conciliacao_casa['Data'].dt.month >= (1)) &
        (df_conciliacao_casa['Data'].dt.month <= (3))
        ]

    elif trim_selecionado == '2º Trimestre':
        df_dias_nao_conciliados_casa = df_conciliacao_casa[
        (df_conciliacao_casa['Data'].dt.year == ano_farol) &
        (df_conciliacao_casa['Data'].dt.month >= (4)) &
        (df_conciliacao_casa['Data'].dt.month <= (6))
        ]

    elif trim_selecionado == '3º Trimestre':
        df_dias_nao_conciliados_casa = df_conciliacao_casa[
        (df_conciliacao_casa['Data'].dt.year == ano_farol) &
        (df_conciliacao_casa['Data'].dt.month >= (7)) &
        (df_conciliacao_casa['Data'].dt.month <= (9))
        ]

    elif trim_selecionado == '4º Trimestre':
        df_dias_nao_conciliados_casa = df_conciliacao_casa[
        (df_conciliacao_casa['Data'].dt.year == ano_farol) &
        (df_conciliacao_casa['Data'].dt.month >= (10)) &
        (df_conciliacao_casa['Data'].dt.month <= (12))
        ]
    
    # Filtra por dias com conciliação != 0
    df_dias_nao_conciliados_casa = df_dias_nao_conciliados_casa[df_dias_nao_conciliados_casa['Conciliação'] != 0.0]
    qtd_dias_nao_conciliados = df_dias_nao_conciliados_casa['Conciliação'].count()
    return df_dias_nao_conciliados_casa, qtd_dias_nao_conciliados


# Gráfico de dias não conciliados por casa e trimestre
def grafico_dias_nao_conciliados_trim(df_conciliacao_farol, casas_validas, trimestre, lista_casas_trim, ano_farol, datas_completas):
    
    # Define as séries (barras) do eixo x (uma para cada casa)
    series = [
        {
            "name": nome,
            "type": "bar",
            "barGap": "10%",
            "data": [lista_casas_trim[i]],
            "label": {
                "show": True,
                "position": "top" 
            },
            "itemStyle": {"color": cores_casas[i]}
        }
        for i, nome in enumerate(casas_validas)
    ]

    grafico_dias_nao_conciliados_trim = {
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "legend": {
            "data": casas_validas,
            "orient": "vertical",   # legenda em coluna
            "right": "0%",        
            "top": "center",
            "backgroundColor": "#ffffff55",
        },
        "grid": {
            "left": "2%", 
            "right": "23%", 
            "bottom": "0%", 
            "containLabel": True},
        "xAxis": [{
            "type": "category", 
            "axisTick": {"show": True}, 
            "data": [trimestre]}],
        "yAxis": [
            {
            "type": "value", 
            "axisLabel": {"formatter": "{value} %"}
            }
        ],
        "series": series
    }

    # Evento de clique - seleciona a casa
    events = {
        "click": "function(params) { return params.seriesName; }"
    }
    
    casa_selecionada = st_echarts(options=grafico_dias_nao_conciliados_trim, events=events, height="550px", width="100%")

    if not casa_selecionada:
        st.warning("Selecione uma casa para visualizar os dias não conciliados")
    else:
        # Exibe dataframe dos dias não conciliados da casa no trimestre
        st.divider()
        st.subheader(f"Dias não conciliados - {casa_selecionada}")
        df_dias_nao_conciliados_casa, qtd_dias_nao_conciliados = dias_nao_conciliados_casa_trim(df_conciliacao_farol, casa_selecionada, trimestre, ano_farol, datas_completas)
        df_dias_nao_conciliados_casa_fmt = formata_df(df_dias_nao_conciliados_casa)
        st.dataframe(df_dias_nao_conciliados_casa_fmt, hide_index=True)
        st.write(f'**Quantidade de dias não conciliados:** {qtd_dias_nao_conciliados}')

