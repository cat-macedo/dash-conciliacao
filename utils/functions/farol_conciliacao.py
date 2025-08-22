import streamlit as st
import pandas as pd
from datetime import datetime
from utils.functions.general_functions import *
from utils.functions.conciliacoes import *
from utils.functions.farol_conciliacao import *
from utils.queries import *

nomes_meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

# Calcula porcentagem de dias conciliados/não conciliados por mês de cada casa
def dias_nao_conciliados_casa(df_casa, ano_farol, df_meses, mes_atual):
    df_dias_nao_conciliados = df_casa[df_casa['Data'].dt.year == ano_farol]
    df_dias_nao_conciliados = df_dias_nao_conciliados[df_dias_nao_conciliados['Conciliação'] != 0.0]
    df_dias_nao_conciliados['Data'] = df_dias_nao_conciliados['Data'].dt.month # Mês dos dias não conciliados

    # Contagem de dias não conciliados por mês
    df_qtd_dias_nao_conciliados_mes = df_dias_nao_conciliados.groupby(['Data'])['Conciliação'].count().reset_index()
    df_qtd_dias_nao_conciliados_mes = df_qtd_dias_nao_conciliados_mes.merge(df_meses, left_on='Data', right_on='Mes', how='right')
    
    # Porcentagem de dias não conciliados por mês 
    df_qtd_dias_nao_conciliados_mes['Porcentagem'] = df_qtd_dias_nao_conciliados_mes['Conciliação'] / df_qtd_dias_nao_conciliados_mes['Qtd_dias']
    df_qtd_dias_nao_conciliados_mes['Porcentagem'] = df_qtd_dias_nao_conciliados_mes['Porcentagem'].fillna(0) # Preenche meses None com zero (tem todos os dias conciliados ou meses depois do atual)

    # Lista com meses (0-11) e a porcentagem de dias não conciliados
    porc_dias_nao_conciliados = df_qtd_dias_nao_conciliados_mes['Porcentagem'].tolist()

    # Lista com meses (0-11) e a porcentagem de dias conciliados 
    lista_dias_nao_conciliados = []
    for i, dia in enumerate(porc_dias_nao_conciliados):
        if i <= mes_atual - 1:
            dia = round((dia * 100), 2)  # 2 casas decimais
        else:
            dia = 0 # meses depois do atual: 0 conciliação
        lista_dias_nao_conciliados.append(dia)

    #st.write(df_dias_nao_conciliados) # vou precisar
    #st.write(df_qtd_dias_nao_conciliados_mes)

    # Criar uma lista de dicionários com os valores e a cor para cada barra (preenche o gráfico)
    # dados_barras_com_cor = []
    # for valor in lista_dias_conciliados:
    #     cor = '#008000' if valor == 100 else '#F1C61A'
    #     dados_barras_com_cor.append({
    #         "value": valor,
    #         "itemStyle": {
    #             "color": cor
    #         }
    #     })
    # lista_dias_nao_conciliados = [v if v != 0 else None for v in lista_dias_nao_conciliados]  # None não é plotado
    return lista_dias_nao_conciliados


# Gráfico exibido ao clicar num mês 
def grafico_dias_nao_conciliados_mes(casas_validas, lista_casas, nome_mes, mes_selecionado):
    for i, casa in enumerate(lista_casas):
        for j, valor in enumerate(casa):
            if valor is None:
                lista_casas[i][j] = 0

    lista_mes = []
    for casa in lista_casas:
        lista_mes.append(casa[mes_selecionado])
    
    cores = [
    "#582310", "#DF2526", "#84161f", "#1C6EBA", "#E9A700", "#FF8800", "#081F5C", "#004080",
    "#336699", "#6699CC", "#4A5129", "#8CA706", "#0CA22E", "#E799BB", "#006E77", "#000000",
    "#C2185B", "#FF6600", "#9933CC", "#330099"
    ]
    
    series = [
        {
            "name": nome,
            "type": "bar",
            "barGap": "10%",
            "data": [lista_mes[i]],
            "backgroundStyle": {
                "color": 'rgba(180, 180, 180, 0.2)'
            },
            "itemStyle": {"color": cores[i]},
            "label": {
                "show": True,
                "position": "top" 
            }
        }
        for i, nome in enumerate(casas_validas)
    ]

    grafico_dias_nao_conciliados_mes = {
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "legend": {"data": casas_validas, "type": "scroll", "bottom": 0},
        "grid": {"left": "4%", "right": "4%", "bottom": "10%", "containLabel": True},
        "xAxis": {
            "type": 'category',
            "data": [nome_mes]
        },
        "yAxis": {
            "type": 'value'
        },
        "series": series
    }

    st_echarts(options=grafico_dias_nao_conciliados_mes, height="600px", width="100%")


# Gráfico com todos os meses e todas as casas
def grafico_dias_nao_conciliados(casas_validas, nomes_meses, lista_casas):
    cores = [
    "#582310", "#DF2526", "#84161f", "#1C6EBA", "#E9A700", "#FF8800", "#081F5C", "#004080",
    "#336699", "#6699CC", "#4A5129", "#8CA706", "#0CA22E", "#E799BB", "#006E77", "#000000",
    "#C2185B", "#FF6600", "#9933CC", "#330099"
    ]

    series = [
        {
            "name": nome,
            "type": "bar",
            "barGap": "10%",
            "data": lista_casas[i],
            "itemStyle": {"color": cores[i]}
        }
        for i, nome in enumerate(casas_validas)
    ]

    grafico_dias_nao_conciliados = {
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "legend": {"data": casas_validas, "type": "scroll", "bottom": 0},
        "grid": {"left": "4%", "right": "4%", "bottom": "10%", "containLabel": True},
        "xAxis": [{"type": "category", "axisTick": {"show": True}, "data": nomes_meses}],
        "yAxis": [{"type": "value", "min": 0, "max": 50, "interval": 10, "axisLabel": {"formatter": "{value} %"}}],
        "series": series
    }

    # Evento de clique - abre o mês
    events = {
        "click": "function(params) { return params.name; }"
    }
    
    mes_selecionado = st_echarts(options=grafico_dias_nao_conciliados, events=events, height="600px", width="100%")
    
    if not mes_selecionado:
        st.warning("Selecione um mês para melhor visualização")
    else: 
        # Exibe gráfico do mês selecionado
        meses = {
            "Jan": "Janeiro",
            "Fev": "Fevereiro",
            "Mar": "Março",
            "Abr": "Abril",
            "Mai": "Maio",
            "Jun": "Junho",
            "Jul": "Julho",
            "Ago": "Agosto",
            "Set": "Setembro",
            "Out": "Outubro",
            "Nov": "Novembro",
            "Dez": "Dezembro"
            }
        
        nome_mes = meses[mes_selecionado]

        for mes in nomes_meses:
            if mes_selecionado == mes:
                mes_selecionado = nomes_meses.index(mes)
        
        st.divider()
        st.subheader(f"% Dias não conciliados por casa - {nome_mes}")
        grafico_dias_nao_conciliados_mes(casas_validas, lista_casas, nome_mes, mes_selecionado)

