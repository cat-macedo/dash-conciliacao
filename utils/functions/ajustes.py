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


def contagem_categorias(df, categoria):
    df_copia = df.copy()
    contagem = int((df_copia['Categoria'] == categoria).sum())
    return contagem


def grafico_pizza_cont_categ(categ1, categ2, categ3, categ4, categ5, categ6):
    grafico_contagem_categ = {
        "tooltip": {
            "trigger": "item"
        },
        "legend": {
            "orient": "vertical",   # legenda em coluna
            "left": "0%",        # pode ser "left", "right" ou número em px
            "top": "center"
        },
        "series": [
            {
                "name": "Contagem de categorias",
                "type": "pie",
                "radius": ["40%", "70%"],
                "center": ["70%", "50%"],
                "avoidLabelOverlap": False,
                "itemStyle": {
                    "borderRadius": 10,
                    "borderColor": "#fff",
                    "borderWidth": 2
                },
                "label": {
                    "show": False,
                    "position": "center"
                },
                "emphasis": {
                    "label": {
                        "show": False,
                        "fontSize": 15,
                        "fontWeight": "bold"
                    }
                },
                "labelLine": {
                    "show": False
                },
                "data": [
                    { "value": categ1, "name": "Tesouraria - Depósito em conta" },
                    { "value": categ2, "name": "Tesouraria - Despesa paga em dinheiro" },
                    { "value": categ3, "name": "Receita de evento recebido via cartão de credito Zigpay/Cielo" },
                    { "value": categ4, "name": "Adição de saldo no cartão pré-pago" },
                    { "value": categ5, "name": "RESG/VENCTO CDB" },
                    { "value": categ6, "name": "APLICACAO CDB" }
                ]
            }
        ]
    }
    st_echarts(options=grafico_contagem_categ, height="300px")


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
    
    # if mes_selecionado:
    #     st.divider()
    #     meses = {
    #     "Jan": "Janeiro",
    #     "Fev": "Fevereiro",
    #     "Mar": "Março",
    #     "Abr": "Abril",
    #     "Mai": "Maio",
    #     "Jun": "Junho",
    #     "Jul": "Julho",
    #     "Ago": "Agosto",
    #     "Set": "Setembro",
    #     "Out": "Outubro",
    #     "Nov": "Novembro",
    #     "Dez": "Dezembro"
    #     }
    #     mes = meses[mes_selecionado]
    #     st.subheader(f"Ajustes - {mes}")

    #     for mes in nomes_meses:
    #         if mes_selecionado == mes:
    #             mes_selecionado = nomes_meses.index(mes) + 1
        
    #     # Exibe df de ajustes do mês selecionado
    #     df_ajustes_formatado = df_ajustes_filtrado[df_ajustes_filtrado['Data_Ajuste'].dt.month == mes_selecionado]
    #     df_ajustes_final = formata_df(df_ajustes_formatado)
    #      st.dataframe(df_ajustes_final, use_container_width=True, hide_index=True)


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
        nome_mes = meses[mes_selecionado]
        st.subheader(f"Ajustes - {nome_mes}")

        for mes in nomes_meses:
            if mes_selecionado == mes:
                mes_selecionado = nomes_meses.index(mes) + 1
        
        # Exibe df de ajustes do mês selecionado
        df_ajustes_formatado = df_ajustes_filtrado[df_ajustes_filtrado['Data_Ajuste'].dt.month == mes_selecionado]
        df_ajustes_final = formata_df(df_ajustes_formatado)
        st.dataframe(df_ajustes_final, use_container_width=True, hide_index=True)

        st.divider()

        # Exibe gráfico de pizza da quantidade de ajustes por categoria
        df_contagem_categ1 = contagem_categorias(df_ajustes_formatado, 'Tesouraria - Depósito em conta')
        df_contagem_categ2 = contagem_categorias(df_ajustes_formatado, 'Tesouraria - Despesa paga em dinheiro')
        df_contagem_categ3 = contagem_categorias(df_ajustes_formatado, 'Receita de evento recebido via cartão de crédito Zigpay/Cielo')
        df_contagem_categ4 = contagem_categorias(df_ajustes_formatado, 'Adição de saldo no cartão pré-pago')
        df_contagem_categ5 = contagem_categorias(df_ajustes_formatado, 'RESG/VENCTO CDB')
        df_contagem_categ6 = contagem_categorias(df_ajustes_formatado, 'APLICACAO CDB')

        st.subheader("Contagem de categorias")
        grafico_categorias = grafico_pizza_cont_categ(df_contagem_categ1, df_contagem_categ2, df_contagem_categ3, df_contagem_categ4, df_contagem_categ5, df_contagem_categ6)
        
