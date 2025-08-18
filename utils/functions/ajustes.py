import streamlit as st
import pandas as pd
import numpy as np
from utils.queries import *
from utils.functions.general_functions import *
from decimal import Decimal
from streamlit_echarts import st_echarts


nomes_meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']


# Filtra tabela de ajustes por casa e ano
def define_df_ajustes(id_casa, ano):
    df_ajustes = st.session_state["df_ajustes_conciliacao"]
    if id_casa != 157:
        df_ajustes_filtrado = df_ajustes[df_ajustes["ID_Casa"] == id_casa]
        df_ajustes_filtrado = df_ajustes_filtrado[df_ajustes_filtrado['Data_Ajuste'].dt.year == ano]
    else: 
        df_ajustes_filtrado = df_ajustes[df_ajustes['Data_Ajuste'].dt.year == ano]

    return df_ajustes_filtrado


def total_ajustes_mes(df_ajustes_filtrado):
    # Pega o mês da data do ajuste
    df_ajustes_filtrado_copia = df_ajustes_filtrado.copy()
    df_ajustes_filtrado_copia['Mes'] = df_ajustes_filtrado_copia['Data_Ajuste'].dt.month

    total_ajustes_mes = df_ajustes_filtrado_copia.groupby(['Mes'])['Valor'].sum().reset_index()
    lista_total_ajustes_mes = total_ajustes_mes['Valor'].tolist()
    lista_total_ajustes_mes = [float(valor) if isinstance(valor, Decimal) else valor for valor in lista_total_ajustes_mes]
    
    # Valor total de ajustes por mês
    lista_total_ajustes_mes_fmt = valores_labels_formatados(lista_total_ajustes_mes) 

    return lista_total_ajustes_mes_fmt


def qtd_ajustes_mes(df_ajustes_filtrado):
    # Pega o mês da data do ajuste
    df_ajustes_filtrado_copia = df_ajustes_filtrado.copy()
    df_ajustes_filtrado_copia['Mes'] = df_ajustes_filtrado_copia['Data_Ajuste'].dt.month

    # Contabiliza ajustes por mês
    df_meses = pd.DataFrame({'Mes': list(range(1, 13)), 'Nome_Mes': nomes_meses})
    df_ajustes_filtrado_copia = df_ajustes_filtrado_copia.merge(df_meses, on='Mes', how='right')

    ajustes_mes = df_ajustes_filtrado_copia.groupby(['Mes'])['Casa'].count().reset_index()
    ajustes_mes.rename(columns = {'Casa':'Qtd_Ajustes'}, inplace=True)

    # Qtd de ajustes por mês
    lista_qtd_ajustes_mes = ajustes_mes['Qtd_Ajustes'].tolist() 
    return lista_qtd_ajustes_mes


def grafico_total_ajustes(df_ajustes_filtrado, lista_total_ajustes_mes_fmt):
    # Gráfico: valor total de ajustes por mês
    grafico_total_ajustes = {
        # "title": {
        #   "text": "Valor total de ajustes por mês"   
        # },
        "tooltip": {
            "trigger": 'axis',
            "axisPointer": {
            "type": 'shadow'
            }
        },
        "grid": {
            "left": "4%",
            "right": "4%",
            "bottom": "0%",
            "containLabel": True
        },
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
            "name": 'Total de Ajustes',
            "type": 'bar',
            "barWidth": "50%",
            "barGap": "5%",
            "data": lista_total_ajustes_mes_fmt,
            "itemStyle": {
                "color": "#F1C61A"
            },
            "label": {
                "show": True,
                "position": "top",
            }
            }
        ]
    }

    # Evento de clique - abre tabela de ajustes detalhada
    events = {
        "click": "function(params) { return params.name; }"
    }

    # Exibe o gráfico
    mes_selecionado = st_echarts(options=grafico_total_ajustes, events=events, height="320px", width="100%")
    
    if mes_selecionado:
        st.divider()
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
        mes = meses[mes_selecionado]
        st.subheader(f"Ajustes - {mes}")

        for mes in nomes_meses:
            if mes_selecionado == mes:
                mes_selecionado = nomes_meses.index(mes) + 1
        
        # Exibe df de ajustes do mês selecionado
        df_ajustes_formatado = df_ajustes_filtrado[df_ajustes_filtrado['Data_Ajuste'].dt.month == mes_selecionado]
        df_ajustes_formatado = formata_df(df_ajustes_formatado)
        st.dataframe(df_ajustes_formatado, use_container_width=True, hide_index=True)


def grafico_ajustes_mes(df_ajustes_filtrado, lista_qtd_ajustes_mes):
    # Gráfico: quantidade de ajustes por mês
    grafico_qtd_ajustes = {
        # "title": {
        #   "text": "Quantidade de ajustes por mês"
        # },
        "tooltip": {
            "trigger": 'axis',
            "axisPointer": {
            "type": 'shadow'
            }
        },
        "grid": {
            "left": "4%",
            "right": "4%",
            "bottom": "0%",
            "containLabel": True
        },
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
            "barWidth": "50%",
            "barGap": "5%",
            "data": lista_qtd_ajustes_mes,
            "itemStyle": {
                "color": "#1C6EBA"
            },
            "label": {
                "show": True,
                "position": "top" 
            }
            }
        ]
    }

    # Evento de clique - abre tabela de ajustes detalhada
    events = {
        "click": "function(params) { return params.name; }"
    }

    # Exibe o gráfico
    mes_selecionado = st_echarts(options=grafico_qtd_ajustes, events=events, height="320px", width="100%")
    
    if not mes_selecionado:
          st.warning("Selecione um mês do gráfico para visualizar os ajustes correspondentes")

    else:
        st.divider()
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
        mes = meses[mes_selecionado]
        st.subheader(f"Ajustes - {mes}")

        for mes in nomes_meses:
            if mes_selecionado == mes:
                mes_selecionado = nomes_meses.index(mes) + 1
        
        # Exibe df de ajustes do mês selecionado
        df_ajustes_formatado = df_ajustes_filtrado[df_ajustes_filtrado['Data_Ajuste'].dt.month == mes_selecionado]
        df_ajustes_formatado = formata_df(df_ajustes_formatado)
        st.dataframe(df_ajustes_formatado, use_container_width=True, hide_index=True)
