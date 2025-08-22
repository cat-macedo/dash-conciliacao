import streamlit as st
import pandas as pd
from datetime import datetime
from utils.functions.general_functions import *
from utils.functions.conciliacoes import *
from utils.queries import *

# Função auxiliar para somar valores agrupados por data
def somar_por_data(df, col_data, col_valor, datas):
    s = df.groupby(col_data)[col_valor].sum()
    # s.index = pd.to_datetime(s.index).date  # garante que o índice é só data
    return s.reindex(datas, fill_value=0).reset_index(drop=True).astype(float)


# Função auxiliar para calcular diferenças de contas a pagar e receber
def calcula_diferencas(df, coluna_principal, colunas_valores):
    soma = 0
    diferenca = 0
    soma = sum(df[col] for col in colunas_valores)
    diferenca = df[coluna_principal] - soma
    return diferenca

# Cria tabela de conciliação para cada casa
def conciliacao_casa(df, casa, datas_completas):
    # df_casas = st.session_state['df_casas']
    # id_casa = df_casas[df_casas['Casa'] == casa]
    # id_casa = id_casa.iloc[0]['ID_Casa']  # pega o ID correspondente
    # st.write(id_casa)

    df_copia = df.copy()

    # # Extrato Zig (Saques) #
    df_extrato_zig = st.session_state['df_extrato_zig']
    df_extrato_zig_farol = df_extrato_zig[df_extrato_zig['Casa'] == casa]
    if 'Extrato Zig (Saques)' not in df_copia.columns:
        df_copia['Extrato Zig (Saques)'] = somar_por_data(
            df_extrato_zig_farol[df_extrato_zig_farol['Descricao'].isin(["Saque", "Antecipação"])],
            "Data_Liquidacao", "Valor", datas_completas
        ) * (-1)

    # Faturam dinheiro #
    if 'Faturam dinheiro' not in df_copia.columns:
        df_copia['Faturam dinheiro'] = 0 # stand-by

    # Receitas Extraordinárias #
    df_parc_receit_extr = st.session_state['df_parc_receit_extr']
    df_parc_receit_extr_farol = df_parc_receit_extr[df_parc_receit_extr['Casa'] == casa]
    if 'Receitas Extraordinárias' not in df_copia.columns:
        df_copia['Receitas Extraordinárias'] = somar_por_data(
            df_parc_receit_extr_farol, "Recebimento_Parcela", "Valor_Parcela", datas_completas
        )

    # Eventos (desmembrar de Receitas Extraordinárias) #
    df_eventos = st.session_state['df_eventos']
    df_eventos_farol = df_eventos[df_eventos['Casa'] == casa]
    if 'Eventos' not in df_copia.columns:
        df_copia['Eventos'] = somar_por_data(
            df_eventos_farol, "Recebimento Parcela", "Valor Parcela", datas_completas
        )

    # Entradas Mutuos #
    df_mutuos = st.session_state['df_mutuos']
    df_mutuos_farol = df_mutuos[(df_mutuos['Casa_Saida'] == casa) | (df_mutuos['Casa_Entrada'] == casa)] 
    if 'Entradas Mútuos' not in df_copia.columns:
        df_copia['Entradas Mútuos'] = somar_por_data(
            df_mutuos_farol[df_mutuos_farol['Casa_Entrada'] == casa], 
            "Data_Mutuo", "Valor", datas_completas
        )

    # Desbloqueios Judiciais #
    df_bloqueios_judiciais = st.session_state['df_bloqueios_judiciais']
    df_bloqueios_judiciais_farol = df_bloqueios_judiciais[df_bloqueios_judiciais['Casa'] == casa]
    if 'Desbloqueios Judiciais' not in df_copia.columns:
        df_copia['Desbloqueios Judiciais'] = somar_por_data(
            df_bloqueios_judiciais_farol[df_bloqueios_judiciais_farol['Valor'] > 0],
            "Data_Transacao", "Valor", datas_completas
        )

    # Extrato Bancário (Crédito) #
    df_extratos_bancarios = st.session_state['df_extratos_bancarios']
    df_extratos_bancarios_farol = df_extratos_bancarios[df_extratos_bancarios['Casa'] == casa]
    if 'Extrato Bancário (Crédito)' not in df_copia.columns:
        df_filtrado = df_extratos_bancarios_farol.copy()
        df_filtrado['Data_Somente'] = pd.to_datetime(df_filtrado['Data_Transacao']).dt.date

        df_copia['Extrato Bancário (Crédito)'] = somar_por_data(
            df_filtrado[df_filtrado['Tipo_Credito_Debito'] == "CREDITO"],
            "Data_Somente",  # ainda usamos a coluna original com hora para somar por data
            "Valor", datas_completas
        )

    # Diferenças (Contas a Receber) #
    if 'Diferenças (Contas a Receber)' not in df.columns:
        df_copia['Diferenças (Contas a Receber)'] = calcula_diferencas(
            df_copia, "Extrato Bancário (Crédito)", ['Extrato Zig (Saques)', 'Faturam dinheiro', 'Receitas Extraordinárias', 'Eventos', 'Entradas Mútuos', 'Desbloqueios Judiciais']
        )

    # Custos sem parcelamento #
    df_custos_blueme_sem_parcelam = st.session_state['df_custos_blueme_sem_parcelam']
    df_custos_blueme_sem_parcelam_farol = df_custos_blueme_sem_parcelam[df_custos_blueme_sem_parcelam['Casa'] == casa]
    if 'Custos sem Parcelamento' not in df_copia.columns:
        df_copia['Custos sem Parcelamento'] = somar_por_data(
            df_custos_blueme_sem_parcelam_farol, "Realizacao_Pgto", "Valor", datas_completas
        ) * (-1)

    # Custos com parcelamento #
    df_custos_blueme_com_parcelam = st.session_state['df_custos_blueme_com_parcelam']
    df_custos_blueme_com_parcelam_farol = df_custos_blueme_com_parcelam[df_custos_blueme_com_parcelam['Casa'] == casa]
    if 'Custos com Parcelamento' not in df_copia.columns:
        df_copia['Custos com Parcelamento'] = somar_por_data(
            df_custos_blueme_com_parcelam_farol, "Realiz_Parcela", "Valor_Parcela", datas_completas
        ) * (-1)

    # Saidas Mutuos #
    if 'Saídas Mútuos' not in df_copia.columns:
        df_copia['Saídas Mútuos'] = somar_por_data(
            df_mutuos_farol[df_mutuos_farol['Casa_Saida'] == casa],
            "Data_Mutuo", "Valor", datas_completas
        ) * (-1)

    # Bloqueios Judiciais #
    if 'Bloqueios Judiciais' not in df_copia.columns:
        df_copia['Bloqueios Judiciais'] = somar_por_data(
            df_bloqueios_judiciais_farol[df_bloqueios_judiciais_farol['Valor'] < 0],
            "Data_Transacao", "Valor", datas_completas
        )

    # Extrato Bancário (Débito) #
    if 'Extrato Bancário (Débito)' not in df_copia.columns:
        df_filtrado = df_extratos_bancarios_farol.copy()
        df_filtrado['Data_Transacao'] = pd.to_datetime(df_filtrado['Data_Transacao']).dt.date

        df_copia['Extrato Bancário (Débito)'] = somar_por_data(
            df_filtrado[df_filtrado['Tipo_Credito_Debito'] == "DEBITO"],
            "Data_Transacao", "Valor", datas_completas
        )

    # Diferenças (Contas a pagar) #
    if 'Diferenças (Contas a Pagar)' not in df_copia.columns:
        df_copia['Diferenças (Contas a Pagar)'] = calcula_diferencas(
            df_copia, "Extrato Bancário (Débito)", ['Custos sem Parcelamento', 'Custos com Parcelamento', 'Saídas Mútuos', 'Bloqueios Judiciais']
        )

    # Ajustes #
    df_ajustes_conciliacao = st.session_state['df_ajustes_conciliacao']
    df_ajustes_conciliacao_farol = df_ajustes_conciliacao[df_ajustes_conciliacao['Casa'] == casa]
    if 'Ajustes Conciliação' not in df_copia.columns:
        df_copia['Ajustes Conciliação'] = somar_por_data(
            df_ajustes_conciliacao_farol, "Data_Ajuste", "Valor", datas_completas
        )

    # Conciliação # 
    if 'Conciliação' not in df_copia.columns:
        df_copia['Conciliação'] = df_copia['Diferenças (Contas a Pagar)'] + df_copia['Diferenças (Contas a Receber)'] - df_copia['Ajustes Conciliação']
    
        # Garante que é float
        df_copia['Conciliação'] = pd.to_numeric(df_copia['Conciliação'], errors='coerce')

        # Zera valores muito pequenos 
        df_copia['Conciliação'] = df_copia['Conciliação'].apply(lambda x: 0.0 if abs(x) < 0.005 else x)

    return df_copia


