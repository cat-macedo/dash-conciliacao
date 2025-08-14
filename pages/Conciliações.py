import streamlit as st
import pandas as pd
import datetime
import calendar
from utils.functions.general_functions import *
from utils.queries import *
from workalendar.america import Brazil


st.set_page_config(
    page_title="Conciliação FB",
    page_icon=":moneybag:",
    layout="wide"
)

# Se der refresh, volta para página de login
if 'loggedIn' not in st.session_state or not st.session_state['loggedIn']:
	st.switch_page('Main.py')

# Personaliza menu lateral
config_sidebar()

st.title(":moneybag: Conciliação FB")
st.divider()


# Filtrando Data
today = datetime.datetime.now()
last_year = today.year - 1
jan_last_year = datetime.datetime(last_year, 1, 1)
jan_this_year = datetime.datetime(today.year, 1, 1)
last_day_of_month = calendar.monthrange(today.year, today.month)[1]
this_month_this_year = datetime.datetime(today.year, today.month, last_day_of_month)
dec_this_year = datetime.datetime(today.year, 12, 31)

## 5 meses atras
month_sub_3 = today.month - 3
year = today.year

if month_sub_3 <= 0:
    # Se o mês resultante for menor ou igual a 0, ajustamos o ano e corrigimos o mês
    month_sub_3 += 12
    year -= 1

start_of_three_months_ago = datetime.datetime(year, month_sub_3, 1)

# Campos de seleção de data
col1, col2 = st.columns(2)

with col1:
    d_inicial = st.date_input("Data de início", value=jan_this_year, min_value=jan_last_year, max_value=dec_this_year, format="DD/MM/YYYY")
with col2:
    d_final = st.date_input("Data de fim", value=this_month_this_year, min_value=jan_last_year, max_value=dec_this_year, format="DD/MM/YYYY")

# Convertendo as datas dos inputs para datetime
start_date = pd.to_datetime(d_inicial)
end_date = pd.to_datetime(d_final)

if start_date > end_date:
    st.warning("A data de fim deve ser maior que a data de início!")
else:

    # Filtrando casas
    df_casas = st.session_state["df_casas"]
    casas = df_casas['Casa'].tolist()
    casa = st.selectbox("Casa", casas)

    # Definindo um dicionário para mapear nomes de casas a IDs de casas
    mapeamento_lojas = dict(zip(df_casas["Casa"], df_casas["ID_Casa"]))

    # Obtendo o ID da casa selecionada
    id_casa = mapeamento_lojas[casa]
    # st.write('ID da casa selecionada:', id_casa)
    if id_casa == 157 or casa == "All bar":
        st.warning("Selecione uma casa")

    st.divider()

    ### Definindo Bases - Filtra por casa e data ###

    ## Extratos Zig
    st.subheader("Extrato Zig")
    df_extrato_zig = st.session_state["df_extrato_zig"]
    # df_extrato_zig_filtrada = df_extrato_zig[df_extrato_zig['ID_Casa'] == id_casa]
    # df_extrato_zig_filtrada = df_extrato_zig_filtrada[(df_extrato_zig_filtrada["Data_Liquidacao"] >= start_date) & (df_extrato_zig_filtrada["Data_Liquidacao"] <= end_date)]
    df_extrato_zig_filtrada, df_extrato_zig_formatada = filtra_formata_df(df_extrato_zig, "Data_Liquidacao", id_casa, start_date, end_date)

    st.dataframe(df_extrato_zig_formatada, use_container_width=True, hide_index=True)
    st.divider()

    ## Zig_Faturamento
    st.subheader("Zig Faturamento")
    df_zig_faturam = st.session_state["df_zig_faturam"]
    # df_zig_faturam_filtrada = df_zig_faturam[df_zig_faturam['ID_Casa'] == id_casa]
    # df_zig_faturam_filtrada = df_zig_faturam_filtrada[(df_zig_faturam_filtrada["Data_Venda"] >= start_date) & (df_zig_faturam_filtrada["Data_Venda"] <= end_date)]
    df_zig_faturam_filtrada, df_zig_faturam_formatada= filtra_formata_df(df_zig_faturam, "Data_Venda", id_casa, start_date, end_date)

    st.dataframe(df_zig_faturam_formatada, use_container_width=True, hide_index=True)
    st.divider()

    ## Parcelas Receitas Extraordinarias
    st.subheader("Parcelas Receitas Extraordinárias")
    df_parc_receit_extr = st.session_state["df_parc_receit_extr"]
    # df_parc_receit_extr_filtrada = df_parc_receit_extr[df_parc_receit_extr['ID_Casa'] == id_casa]
    # df_parc_receit_extr_filtrada = df_parc_receit_extr_filtrada[(df_parc_receit_extr_filtrada["Recebimento_Parcela"] >= start_date) & (df_parc_receit_extr_filtrada["Recebimento_Parcela"] <= end_date)]
    df_parc_receit_extr_filtrada, df_parc_receit_extr_formatada = filtra_formata_df(df_parc_receit_extr, "Recebimento_Parcela", id_casa, start_date, end_date)

    st.dataframe(df_parc_receit_extr_formatada, use_container_width=True, hide_index=True)
    st.divider()

    ## Custos BlueMe Sem Parcelamento
    st.subheader("Despesas BlueMe Sem Parcelamento")
    df_custos_blueme_sem_parcelam = st.session_state["df_custos_blueme_sem_parcelam"]
    # df_custos_blueme_sem_parcelam_filtrada = df_custos_blueme_sem_parcelam[df_custos_blueme_sem_parcelam['ID_Casa'] == id_casa]
    # df_custos_blueme_sem_parcelam_filtrada = df_custos_blueme_sem_parcelam_filtrada[(df_custos_blueme_sem_parcelam_filtrada["Realizacao_Pgto"] >= start_date) & (df_custos_blueme_sem_parcelam_filtrada["Realizacao_Pgto"] <= end_date)]
    df_custos_blueme_sem_parcelam_filtrada, df_custos_blueme_sem_parcelam_formatada = filtra_formata_df(df_custos_blueme_sem_parcelam, "Realizacao_Pgto", id_casa, start_date, end_date)

    st.dataframe(df_custos_blueme_sem_parcelam_formatada, use_container_width=True, hide_index=True)
    st.divider()

    ## Custos BlueMe Com Parcelamento
    st.subheader("Despesas BlueMe Com Parcelamento")
    df_custos_blueme_com_parcelam = st.session_state["df_custos_blueme_com_parcelam"]
    # df_custos_blueme_com_parcelam_filtrada = df_custos_blueme_com_parcelam[df_custos_blueme_com_parcelam['ID_Casa'] == id_casa]
    # df_custos_blueme_com_parcelam_filtrada = df_custos_blueme_com_parcelam_filtrada[(df_custos_blueme_com_parcelam_filtrada["Realiz_Parcela"] >= start_date) & (df_custos_blueme_com_parcelam_filtrada["Realiz_Parcela"] <= end_date)] 
    df_custos_blueme_com_parcelam_filtrada, df_custos_blueme_com_parcelam_formatada = filtra_formata_df(df_custos_blueme_com_parcelam, "Realiz_Parcela", id_casa, start_date, end_date)

    st.dataframe(df_custos_blueme_com_parcelam_formatada, use_container_width=True, hide_index=True)
    st.divider()

    ## Extratos Bancarios
    st.subheader("Extratos Bancários")
    df_extratos_bancarios = st.session_state["df_extratos_bancarios"]
    # df_extratos_bancarios_filtrada = df_extratos_bancarios[df_extratos_bancarios['ID_Casa'] == id_casa]
    # df_extratos_bancarios_filtrada = df_extratos_bancarios_filtrada[(df_extratos_bancarios_filtrada["Data_Transacao"] >= start_date) & (df_extratos_bancarios_filtrada["Data_Transacao"] <= end_date)] 
    df_extratos_bancarios_filtrada, df_extratos_bancarios_formatada = filtra_formata_df(df_extratos_bancarios, "Data_Transacao", id_casa, start_date, end_date)

    st.dataframe(df_extratos_bancarios_formatada, use_container_width=True, hide_index=True)
    st.divider()

    ## Mutuos
    st.subheader("Mútuos")
    df_mutuos = st.session_state["df_mutuos"]
    df_mutuos_filtrada = df_mutuos[(df_mutuos['ID_Casa_Saida'] == id_casa) | (df_mutuos['ID_Casa_Entrada'] == id_casa)] 
    df_mutuos_filtrada = df_mutuos_filtrada[(df_mutuos["Data_Mutuo"] >= start_date) & (df_mutuos_filtrada["Data_Mutuo"] <= end_date)] 
   
   # Copia para formatação brasileira de colunas numéricas 
    df_mutuos_formatada = df_mutuos_filtrada.copy() 
    
    # Aplica formatação brasileira em colunas numéricas 
    for col in df_mutuos_formatada.select_dtypes(include='object').columns: 
        if col != "Doc_NF":
            df_mutuos_formatada[col] = df_mutuos_formatada[col].apply(format_brazilian) 
    
    # Aplica formatação brasileira em colunas de data 
    for col in df_mutuos_formatada.select_dtypes(include='datetime').columns: 
        df_mutuos_formatada[col] = pd.to_datetime(df_mutuos_formatada[col]).dt.strftime('%d-%m-%Y %H:%M') 
    
    st.dataframe(df_mutuos_formatada, use_container_width=True, hide_index=True)
    st.divider()

    ## Tesouraria
    st.subheader("Tesouraria")
    df_tesouraria = st.session_state["df_tesouraria"]
    # df_tesouraria_filtrada = df_tesouraria[df_tesouraria['ID_Casa'] == id_casa]
    # df_tesouraria_filtrada = df_tesouraria_filtrada[(df_tesouraria_filtrada["Data_Transacao"] >= start_date) & (df_tesouraria_filtrada["Data_Transacao"] <= end_date)] 
    df_tesouraria_filtrada, df_tesouraria_formatada = filtra_formata_df(df_tesouraria, "Data_Transacao", id_casa, start_date, end_date)

    st.dataframe(df_tesouraria_formatada, use_container_width=True, hide_index=True)
    st.divider()

    ## Ajustes Conciliação
    st.subheader("Ajustes Conciliação")
    df_ajustes_conciliacao = st.session_state["df_ajustes_conciliacao"]
    # df_ajustes_conciliacao_filtrada = df_ajustes_conciliacao[df_ajustes_conciliacao['ID_Casa'] == id_casa]
    # df_ajustes_conciliacao_filtrada = df_ajustes_conciliacao_filtrada[(df_ajustes_conciliacao_filtrada["Data_Ajuste"] >= start_date) & (df_ajustes_conciliacao_filtrada["Data_Ajuste"] <= end_date)] 
    df_ajustes_conciliacao_filtrada, df_ajustes_conciliacao_formatada = filtra_formata_df(df_ajustes_conciliacao, "Data_Ajuste", id_casa, start_date, end_date)

    st.dataframe(df_ajustes_conciliacao_formatada, use_container_width=True, hide_index=True)
    st.divider()

    ## Bloqueios Judiciais
    st.subheader("Bloqueios Judiciais")
    df_bloqueios_judiciais = st.session_state["df_bloqueios_judiciais"]
    # df_bloqueios_judiciais_filtrada = df_bloqueios_judiciais[df_bloqueios_judiciais['ID_Casa'] == id_casa]
    # df_bloqueios_judiciais_filtrada = df_bloqueios_judiciais_filtrada[(df_bloqueios_judiciais_filtrada["Data_Transacao"] >= start_date) & (df_bloqueios_judiciais_filtrada["Data_Transacao"] <= end_date)] 
    df_bloqueios_judiciais_filtrada, df_bloqueios_judiciais_formatada = filtra_formata_df(df_bloqueios_judiciais, "Data_Transacao", id_casa, start_date, end_date)

    st.dataframe(df_bloqueios_judiciais_formatada, use_container_width=True, hide_index=True)
    st.divider()   

    ## Eventos
    st.subheader("Eventos")
    df_eventos = st.session_state["df_eventos"]
    # df_eventos_filtrada = df_eventos[df_eventos['ID_Casa'] == id_casa]
    # df_eventos_filtrada = df_eventos_filtrada[(df_eventos_filtrada["Recebimento Parcela"] >= start_date) & (df_eventos_filtrada["Recebimento Parcela"] <= end_date)] 
    df_eventos_filtrada, df_eventos_formatada = filtra_formata_df(df_eventos, "Recebimento Parcela", id_casa, start_date, end_date)

    st.dataframe(df_eventos_formatada, use_container_width=True, hide_index=True)
    st.divider() 


    ## Planilha de Conciliação
    st.subheader("Conciliação")

    # Criar um DataFrame com todas as datas do período selecionado
    df_conciliacao = pd.DataFrame()

    if 'Data' not in df_conciliacao.columns:
        datas = pd.date_range(start=start_date, end=end_date)
        df_conciliacao['Data'] = datas


    # Colunas 

    # Extrato Zig (Saques) #
    if 'Extrato Zig (Saques)' not in df_conciliacao.columns:
        df_conciliacao['Extrato Zig (Saques)'] = somar_por_data(
            df_extrato_zig_filtrada[df_extrato_zig_filtrada['Descricao'].isin(["Saque", "Antecipação"])],
            "Data_Liquidacao", "Valor", datas
        ) * (-1)

    # Faturam dinheiro #
    if 'Faturam dinheiro' not in df_conciliacao.columns:
        df_conciliacao['Faturam dinheiro'] = 0 # stand-by

    # Receitas Extraordinárias #
    if 'Receitas Extraordinárias' not in df_conciliacao.columns:
        df_conciliacao['Receitas Extraordinárias'] = somar_por_data(
            df_parc_receit_extr_filtrada, "Recebimento_Parcela", "Valor_Parcela", datas
        )

    # Eventos (desmembrar de Receitas Extraordinárias) -> stand-by #
    if 'Eventos' not in df_conciliacao.columns:
        df_conciliacao['Eventos'] = somar_por_data(
            df_eventos_filtrada, "Recebimento Parcela", "Valor Parcela", datas
        )

    # Entradas Mutuos #
    if 'Entradas Mútuos' not in df_conciliacao.columns:
        df_conciliacao['Entradas Mútuos'] = somar_por_data(
            df_mutuos_filtrada[df_mutuos_filtrada['Casa_Entrada'] == casa], 
            "Data_Mutuo", "Valor", datas
        )

    # Desbloqueios Judiciais #
    if 'Desbloqueios Judiciais' not in df_conciliacao.columns:
        df_conciliacao['Desbloqueios Judiciais'] = somar_por_data(
            df_bloqueios_judiciais_filtrada[df_bloqueios_judiciais_filtrada['Valor'] > 0],
            "Data_Transacao", "Valor", datas
        )

    # Extrato Bancário (Crédito) #
    if 'Extrato Bancário (Crédito)' not in df_conciliacao.columns:
        df_filtrado = df_extratos_bancarios_filtrada.copy()
        df_filtrado['Data_Somente'] = pd.to_datetime(df_filtrado['Data_Transacao']).dt.date

        df_conciliacao['Extrato Bancário (Crédito)'] = somar_por_data(
            df_filtrado[df_filtrado['Tipo_Credito_Debito'] == "CREDITO"],
            "Data_Somente",  # ainda usamos a coluna original com hora para somar por data
            "Valor", datas
        )

    # Diferenças (Contas a Receber) #
    if 'Diferenças (Contas a Receber)' not in df_conciliacao.columns:
        df_conciliacao['Diferenças (Contas a Receber)'] = calcula_diferencas(
            df_conciliacao, "Extrato Bancário (Crédito)", ['Extrato Zig (Saques)', 'Faturam dinheiro', 'Receitas Extraordinárias', 'Eventos', 'Entradas Mútuos', 'Desbloqueios Judiciais']
        )

    # Custos sem parcelamento #
    if 'Custos sem Parcelamento' not in df_conciliacao.columns:
        df_conciliacao['Custos sem Parcelamento'] = somar_por_data(
            df_custos_blueme_sem_parcelam_filtrada, "Realizacao_Pgto", "Valor", datas
        ) * (-1)

    # Custos com parcelamento #
    if 'Custos com Parcelamento' not in df_conciliacao.columns:
        df_conciliacao['Custos com Parcelamento'] = somar_por_data(
            df_custos_blueme_com_parcelam_filtrada, "Realiz_Parcela", "Valor_Parcela", datas
        ) * (-1)

    # Saidas Mutuos #
    if 'Saídas Mútuos' not in df_conciliacao.columns:
        df_conciliacao['Saídas Mútuos'] = somar_por_data(
            df_mutuos_filtrada[df_mutuos_filtrada['Casa_Saida'] == casa],
            "Data_Mutuo", "Valor", datas
        ) * (-1)

    # Bloqueios Judiciais #
    if 'Bloqueios Judiciais' not in df_conciliacao.columns:
        df_conciliacao['Bloqueios Judiciais'] = somar_por_data(
            df_bloqueios_judiciais_filtrada[df_bloqueios_judiciais_filtrada['Valor'] < 0],
            "Data_Transacao", "Valor", datas
        )

    # Extrato Bancário (Débito) #
    if 'Extrato Bancário (Débito)' not in df_conciliacao.columns:
        df_filtrado = df_extratos_bancarios_filtrada.copy()
        df_filtrado['Data_Transacao'] = pd.to_datetime(df_filtrado['Data_Transacao']).dt.date

        df_conciliacao['Extrato Bancário (Débito)'] = somar_por_data(
            df_filtrado[df_filtrado['Tipo_Credito_Debito'] == "DEBITO"],
            "Data_Transacao", "Valor", datas
        )

    # Diferenças (Contas a pagar) #
    if 'Diferenças (Contas a Pagar)' not in df_conciliacao.columns:
        df_conciliacao['Diferenças (Contas a Pagar)'] = calcula_diferencas(
            df_conciliacao, "Extrato Bancário (Débito)", ['Custos sem Parcelamento', 'Custos com Parcelamento', 'Saídas Mútuos', 'Bloqueios Judiciais']
        )

    # Ajustes #
    if 'Ajustes Conciliação' not in df_conciliacao.columns:
        df_conciliacao['Ajustes Conciliação'] = somar_por_data(
            df_ajustes_conciliacao_filtrada, "Data_Ajuste", "Valor", datas
        )

    # Conciliação # 
    if 'Conciliação' not in df_conciliacao.columns:
        df_conciliacao['Conciliação'] = df_conciliacao['Diferenças (Contas a Pagar)'] + df_conciliacao['Diferenças (Contas a Receber)'] - df_conciliacao['Ajustes Conciliação']


    # Copia para formatação brasileira de colunas numéricas
    df_formatado = df_conciliacao.copy()

    # Aplica formatação brasileira em colunas numéricas
    for col in df_formatado.select_dtypes(include='number').columns:
        df_formatado[col] = df_formatado[col].apply(format_brazilian)

    # Aplica formatação brasileira em colunas de data
    for col in df_formatado.select_dtypes(include='datetime').columns:
        df_formatado[col] = pd.to_datetime(df_formatado[col]).dt.strftime('%d-%m-%Y')


    # Exibe a tabela de conciliação
    if id_casa == 157:
        st.warning("Para visualizar a conciliação, selecione uma casa")
        df_formatado = df_formatado
    else: 
        st.dataframe(df_formatado, use_container_width=True, hide_index=True)

    st.divider()

    ## Exportando em Excel

    excel_filename = 'Conciliacao_FB.xlsx'

    if st.button('Atualizar Planilha Excel'):
        sheet_name_zig = 'df_extrato_zig'
        export_to_excel(df_extrato_zig_filtrada, sheet_name_zig, excel_filename)

        sheet_name_zig = 'df_zig_faturam'
        export_to_excel(df_zig_faturam_filtrada, sheet_name_zig, excel_filename)  

        sheet_name_view_parc_agrup = 'view_parc_agrup'
        export_to_excel(df_parc_receit_extr_filtrada, sheet_name_view_parc_agrup, excel_filename)

        sheet_name_custos_blueme_sem_parcelamento = 'df_blueme_sem_parcelamento'
        export_to_excel(df_custos_blueme_sem_parcelam_filtrada, sheet_name_custos_blueme_sem_parcelamento, excel_filename)

        sheet_name_custos_blueme_com_parcelamento = 'df_blueme_com_parcelamento'
        export_to_excel(df_custos_blueme_com_parcelam_filtrada, sheet_name_custos_blueme_com_parcelamento, excel_filename)

        sheet_name_extratos = 'df_extratos'
        export_to_excel(df_extratos_bancarios_filtrada, sheet_name_extratos, excel_filename)

        df_mutuos_filtrada['Valor_Entrada'] = df_mutuos_filtrada.apply(lambda row: row['Valor'] if row['ID_Casa_Entrada'] == id_casa else 0, axis=1)
        df_mutuos_filtrada['Valor_Saida'] = df_mutuos_filtrada.apply(lambda row: row['Valor'] if row['ID_Casa_Saida'] == id_casa else 0, axis=1)
        df_mutuos_filtrada = df_mutuos_filtrada.drop('Valor', axis=1)
        sheet_name_mutuos = 'df_mutuos'
        export_to_excel(df_mutuos_filtrada, sheet_name_mutuos, excel_filename)

        sheet_name_tesouraria = 'df_tesouraria_trans'
        export_to_excel(df_tesouraria_filtrada, sheet_name_tesouraria, excel_filename)

        sheet_name_ajustes_conciliacao = 'df_ajustes_conciliaco'
        export_to_excel(df_ajustes_conciliacao_filtrada, sheet_name_ajustes_conciliacao, excel_filename)
        
        sheet_name_bloqueios_judiciais = 'df_bloqueios_judiciais'
        export_to_excel(df_bloqueios_judiciais_filtrada, sheet_name_bloqueios_judiciais, excel_filename)  

        st.success('Arquivo atualizado com sucesso!')


    # Botão de Download Direto
    if os.path.exists(excel_filename):
        with open(excel_filename, "rb") as file:
            file_content = file.read()
            st.download_button(
            label="Baixar Excel",
            data=file_content,
            file_name=f"Conciliacao_FB - {casa}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

