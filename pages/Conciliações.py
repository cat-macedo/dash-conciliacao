import streamlit as st
import pandas as pd
from datetime import datetime
import calendar
from utils.functions.general_functions import *
from utils.functions.conciliacoes import *
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
today = datetime.now()
last_year = today.year - 1
jan_last_year = datetime(last_year, 1, 1)
jan_this_year = datetime(today.year, 1, 1)
last_day_of_month = calendar.monthrange(today.year, today.month)[1]
this_month_this_year = datetime(today.year, today.month, last_day_of_month)
dec_this_year = datetime(today.year, 12, 31)

## 5 meses atras
month_sub_3 = today.month - 3
year = today.year

if month_sub_3 <= 0:
    # Se o mês resultante for menor ou igual a 0, ajustamos o ano e corrigimos o mês
    month_sub_3 += 12
    year -= 1

start_of_three_months_ago = datetime(year, month_sub_3, 1)

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
    
    # Troca o valor na lista
    casas = ["Todas as casas" if c == "All bar" else c for c in casas]
    casa = st.selectbox("Casa", casas)
    if casa == "Todas as casas":
        casa = "All bar"

    # Definindo um dicionário para mapear nomes de casas a IDs de casas
    mapeamento_casas = dict(zip(df_casas["Casa"], df_casas["ID_Casa"]))

    # Obtendo o ID da casa selecionada
    id_casa = mapeamento_casas[casa]
    
    st.divider()

    ### Definindo Bases - Filtra por casa e data ###

    ## Extratos Zig
    st.subheader("Extrato Zig")
    df_extrato_zig = st.session_state["df_extrato_zig"]
    df_extrato_zig_filtrada, df_extrato_zig_formatada = filtra_formata_df(df_extrato_zig, "Data_Liquidacao", id_casa, start_date, end_date)

    st.dataframe(df_extrato_zig_formatada, use_container_width=True, hide_index=True)
    st.divider()

    ## Zig_Faturamento
    st.subheader("Zig Faturamento")
    df_zig_faturam = st.session_state["df_zig_faturam"]
    df_zig_faturam_filtrada, df_zig_faturam_formatada= filtra_formata_df(df_zig_faturam, "Data_Venda", id_casa, start_date, end_date)

    st.dataframe(df_zig_faturam_formatada, use_container_width=True, hide_index=True)
    st.divider()

    ## Parcelas Receitas Extraordinarias
    st.subheader("Parcelas Receitas Extraordinárias")
    df_parc_receit_extr = st.session_state["df_parc_receit_extr"]
    df_parc_receit_extr_filtrada, df_parc_receit_extr_formatada = filtra_formata_df(df_parc_receit_extr, "Recebimento_Parcela", id_casa, start_date, end_date)

    st.dataframe(df_parc_receit_extr_formatada, use_container_width=True, hide_index=True)
    st.divider()

    ## Custos BlueMe Sem Parcelamento
    st.subheader("Despesas BlueMe Sem Parcelamento")
    df_custos_blueme_sem_parcelam = st.session_state["df_custos_blueme_sem_parcelam"]
    df_custos_blueme_sem_parcelam_filtrada, df_custos_blueme_sem_parcelam_formatada = filtra_formata_df(df_custos_blueme_sem_parcelam, "Realizacao_Pgto", id_casa, start_date, end_date)

    st.dataframe(df_custos_blueme_sem_parcelam_formatada, use_container_width=True, hide_index=True)
    st.divider()

    ## Custos BlueMe Com Parcelamento
    st.subheader("Despesas BlueMe Com Parcelamento")
    df_custos_blueme_com_parcelam = st.session_state["df_custos_blueme_com_parcelam"]
    df_custos_blueme_com_parcelam_filtrada, df_custos_blueme_com_parcelam_formatada = filtra_formata_df(df_custos_blueme_com_parcelam, "Realiz_Parcela", id_casa, start_date, end_date)

    st.dataframe(df_custos_blueme_com_parcelam_formatada, use_container_width=True, hide_index=True)
    st.divider()

    ## Extratos Bancarios
    st.subheader("Extratos Bancários")
    df_extratos_bancarios = st.session_state["df_extratos_bancarios"]
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
    df_tesouraria_filtrada, df_tesouraria_formatada = filtra_formata_df(df_tesouraria, "Data_Transacao", id_casa, start_date, end_date)

    st.dataframe(df_tesouraria_formatada, use_container_width=True, hide_index=True)
    st.divider()

    ## Ajustes Conciliação
    st.subheader("Ajustes Conciliação")
    df_ajustes_conciliacao = st.session_state["df_ajustes_conciliacao"]
    df_ajustes_conciliacao_filtrada, df_ajustes_conciliacao_formatada = filtra_formata_df(df_ajustes_conciliacao, "Data_Ajuste", id_casa, start_date, end_date)

    st.dataframe(df_ajustes_conciliacao_formatada, use_container_width=True, hide_index=True)
    st.divider()

    ## Bloqueios Judiciais
    st.subheader("Bloqueios Judiciais")
    df_bloqueios_judiciais = st.session_state["df_bloqueios_judiciais"]
    df_bloqueios_judiciais_filtrada, df_bloqueios_judiciais_formatada = filtra_formata_df(df_bloqueios_judiciais, "Data_Transacao", id_casa, start_date, end_date)

    st.dataframe(df_bloqueios_judiciais_formatada, use_container_width=True, hide_index=True)
    st.divider()   

    ## Eventos
    st.subheader("Eventos")
    df_eventos = st.session_state["df_eventos"]
    df_eventos_filtrada, df_eventos_formatada = filtra_formata_df(df_eventos, "Recebimento Parcela", id_casa, start_date, end_date)

    st.dataframe(df_eventos_formatada, use_container_width=True, hide_index=True)
    st.divider() 


    ## Planilha de Conciliação
    st.subheader("Conciliação")

    # Criar um DataFrame com todas as datas do período selecionado
    df_conciliacao = pd.DataFrame()
    st.session_state['df_conciliacao'] = None

    if 'Data' not in df_conciliacao.columns:
        datas = pd.date_range(start=start_date, end=end_date)
        df_conciliacao['Data'] = datas
    
    # Conciliação completa
    datas_completas = pd.date_range(start=jan_last_year, end=dec_this_year)
    df_conciliacao_completa = pd.DataFrame({'Data': datas_completas})

    ## Agrupar por data e casa
    # if casa == "All bar":
    #     df_casas_temp = pd.DataFrame({'Casa': df_casas['Casa']})
    #     df_datas_temp = pd.DataFrame({'Data': datas})
    #     df_conciliacao = pd.merge(df_datas_temp.assign(key=1), df_casas_temp.assign(key=1), on='key').drop('key', axis=1)
    # else:
    #     df_datas_temp = pd.DataFrame({'Data': datas})


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

    # Eventos (desmembrar de Receitas Extraordinárias) #
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
        
        # Garante que é float
        df_conciliacao['Conciliação'] = pd.to_numeric(df_conciliacao['Conciliação'], errors='coerce')

        # Zera valores muito pequenos 
        df_conciliacao['Conciliação'] = df_conciliacao['Conciliação'].apply(lambda x: 0.0 if abs(x) < 0.005 else x)


    # Copia para formatação brasileira de colunas numéricas
    df_formatado = df_conciliacao.copy()

    # Aplica formatação brasileira em colunas numéricas
    for col in df_formatado.select_dtypes(include='number').columns:
        df_formatado[col] = df_formatado[col].apply(format_brazilian)

    # Aplica formatação brasileira em colunas de data
    for col in df_formatado.select_dtypes(include='datetime').columns:
        df_formatado[col] = pd.to_datetime(df_formatado[col]).dt.strftime('%d-%m-%Y')


    # Exibe a tabela de conciliação
    # if id_casa == 157:
    #     st.warning("Para visualizar a conciliação, selecione uma casa")
    #     df_formatado = df_formatado
    # else: 
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
            
    st.divider()

    # Farol de conciliação
    st.subheader("🚦 Farol de conciliação")

    # Filtrando por casa e ano
    col1, col2 = st.columns(2)

    # Seletor de casa
    with col1: 
        df_casas = st.session_state["df_casas"]
        casas = df_casas['Casa'].tolist()

        casas = ["Todas as casas" if c == "All bar" else c for c in casas]
        casa_farol = st.selectbox("Selecione uma casa:", casas)
        if casa_farol == "Todas as casas":
            casa_farol = "All bar"

    # Definindo um dicionário para mapear nomes de casas a IDs de casas
    mapeamento_casas = dict(zip(df_casas["Casa"], df_casas["ID_Casa"]))

    # Obtendo o ID da casa selecionada
    id_casa_farol = mapeamento_casas[casa_farol]

    # Seletor de ano
    with col2:
        ano_atual = datetime.now().year 
        anos = list(range(2024, ano_atual+1))
        index_padrao = anos.index(ano_atual)
        ano_farol = st.selectbox("Selecione um ano:", anos, index=index_padrao)

    st.divider()

    # Conciliação completa (2024 a 2025)
    # Extrato Zig (Saques) #
    df_extrato_zig_farol = df_extrato_zig[df_extrato_zig['ID_Casa'] == id_casa_farol]
    if 'Extrato Zig (Saques)' not in df_conciliacao_completa.columns:
        df_conciliacao_completa['Extrato Zig (Saques)'] = somar_por_data(
            df_extrato_zig_farol[df_extrato_zig_farol['Descricao'].isin(["Saque", "Antecipação"])],
            "Data_Liquidacao", "Valor", datas_completas
        ) * (-1)

    # Faturam dinheiro #
    if 'Faturam dinheiro' not in df_conciliacao_completa.columns:
        df_conciliacao_completa['Faturam dinheiro'] = 0 # stand-by

    # Receitas Extraordinárias #
    df_parc_receit_extr_farol = df_parc_receit_extr[df_parc_receit_extr['ID_Casa'] == id_casa_farol]
    if 'Receitas Extraordinárias' not in df_conciliacao_completa.columns:
        df_conciliacao_completa['Receitas Extraordinárias'] = somar_por_data(
            df_parc_receit_extr_farol, "Recebimento_Parcela", "Valor_Parcela", datas_completas
        )

    # Eventos (desmembrar de Receitas Extraordinárias) #
    df_eventos_farol = df_eventos[df_eventos['ID_Casa'] == id_casa_farol]
    if 'Eventos' not in df_conciliacao_completa.columns:
        df_conciliacao_completa['Eventos'] = somar_por_data(
            df_eventos_farol, "Recebimento Parcela", "Valor Parcela", datas_completas
        )

    # Entradas Mutuos #
    df_mutuos_farol = df_mutuos[(df_mutuos['ID_Casa_Saida'] == id_casa_farol) | (df_mutuos['ID_Casa_Entrada'] == id_casa_farol)] 
    if 'Entradas Mútuos' not in df_conciliacao_completa.columns:
        df_conciliacao_completa['Entradas Mútuos'] = somar_por_data(
            df_mutuos_farol[df_mutuos_farol['Casa_Entrada'] == casa_farol], 
            "Data_Mutuo", "Valor", datas_completas
        )

    # Desbloqueios Judiciais #
    df_bloqueios_judiciais_farol = df_bloqueios_judiciais[df_bloqueios_judiciais['ID_Casa'] == id_casa_farol]
    if 'Desbloqueios Judiciais' not in df_conciliacao_completa.columns:
        df_conciliacao_completa['Desbloqueios Judiciais'] = somar_por_data(
            df_bloqueios_judiciais_farol[df_bloqueios_judiciais_farol['Valor'] > 0],
            "Data_Transacao", "Valor", datas_completas
        )

    # Extrato Bancário (Crédito) #
    df_extratos_bancarios_farol = df_extratos_bancarios[df_extratos_bancarios['ID_Casa'] == id_casa_farol]
    if 'Extrato Bancário (Crédito)' not in df_conciliacao_completa.columns:
        df_filtrado = df_extratos_bancarios_farol.copy()
        df_filtrado['Data_Somente'] = pd.to_datetime(df_filtrado['Data_Transacao']).dt.date

        df_conciliacao_completa['Extrato Bancário (Crédito)'] = somar_por_data(
            df_filtrado[df_filtrado['Tipo_Credito_Debito'] == "CREDITO"],
            "Data_Somente",  # ainda usamos a coluna original com hora para somar por data
            "Valor", datas_completas
        )

    # Diferenças (Contas a Receber) #
    if 'Diferenças (Contas a Receber)' not in df_conciliacao_completa.columns:
        df_conciliacao_completa['Diferenças (Contas a Receber)'] = calcula_diferencas(
            df_conciliacao_completa, "Extrato Bancário (Crédito)", ['Extrato Zig (Saques)', 'Faturam dinheiro', 'Receitas Extraordinárias', 'Eventos', 'Entradas Mútuos', 'Desbloqueios Judiciais']
        )

    # Custos sem parcelamento #
    df_custos_blueme_sem_parcelam_farol = df_custos_blueme_sem_parcelam[df_custos_blueme_sem_parcelam['ID_Casa'] == id_casa_farol]
    if 'Custos sem Parcelamento' not in df_conciliacao_completa.columns:
        df_conciliacao_completa['Custos sem Parcelamento'] = somar_por_data(
            df_custos_blueme_sem_parcelam_farol, "Realizacao_Pgto", "Valor", datas_completas
        ) * (-1)

    # Custos com parcelamento #
    df_custos_blueme_com_parcelam_farol = df_custos_blueme_com_parcelam[df_custos_blueme_com_parcelam['ID_Casa'] == id_casa_farol]
    if 'Custos com Parcelamento' not in df_conciliacao_completa.columns:
        df_conciliacao_completa['Custos com Parcelamento'] = somar_por_data(
            df_custos_blueme_com_parcelam_farol, "Realiz_Parcela", "Valor_Parcela", datas_completas
        ) * (-1)

    # Saidas Mutuos #
    if 'Saídas Mútuos' not in df_conciliacao_completa.columns:
        df_conciliacao_completa['Saídas Mútuos'] = somar_por_data(
            df_mutuos_farol[df_mutuos_farol['Casa_Saida'] == casa_farol],
            "Data_Mutuo", "Valor", datas_completas
        ) * (-1)

    # Bloqueios Judiciais #
    if 'Bloqueios Judiciais' not in df_conciliacao_completa.columns:
        df_conciliacao_completa['Bloqueios Judiciais'] = somar_por_data(
            df_bloqueios_judiciais_farol[df_bloqueios_judiciais_farol['Valor'] < 0],
            "Data_Transacao", "Valor", datas_completas
        )

    # Extrato Bancário (Débito) #
    if 'Extrato Bancário (Débito)' not in df_conciliacao_completa.columns:
        df_filtrado = df_extratos_bancarios_farol.copy()
        df_filtrado['Data_Transacao'] = pd.to_datetime(df_filtrado['Data_Transacao']).dt.date

        df_conciliacao_completa['Extrato Bancário (Débito)'] = somar_por_data(
            df_filtrado[df_filtrado['Tipo_Credito_Debito'] == "DEBITO"],
            "Data_Transacao", "Valor", datas_completas
        )

    # Diferenças (Contas a pagar) #
    if 'Diferenças (Contas a Pagar)' not in df_conciliacao_completa.columns:
        df_conciliacao_completa['Diferenças (Contas a Pagar)'] = calcula_diferencas(
            df_conciliacao_completa, "Extrato Bancário (Débito)", ['Custos sem Parcelamento', 'Custos com Parcelamento', 'Saídas Mútuos', 'Bloqueios Judiciais']
        )

    # Ajustes #
    df_ajustes_conciliacao_farol = df_ajustes_conciliacao[df_ajustes_conciliacao['ID_Casa'] == id_casa_farol]
    if 'Ajustes Conciliação' not in df_conciliacao_completa.columns:
        df_conciliacao_completa['Ajustes Conciliação'] = somar_por_data(
            df_ajustes_conciliacao_farol, "Data_Ajuste", "Valor", datas_completas
        )

    # Conciliação # 
    if 'Conciliação' not in df_conciliacao_completa.columns:
        df_conciliacao_completa['Conciliação'] = df_conciliacao_completa['Diferenças (Contas a Pagar)'] + df_conciliacao_completa['Diferenças (Contas a Receber)'] - df_conciliacao_completa['Ajustes Conciliação']
        
        # Garante que é float
        df_conciliacao_completa['Conciliação'] = pd.to_numeric(df_conciliacao_completa['Conciliação'], errors='coerce')

        # Zera valores muito pequenos 
        df_conciliacao_completa['Conciliação'] = df_conciliacao_completa['Conciliação'].apply(lambda x: 0.0 if abs(x) < 0.005 else x)


    nomes_meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    meses = list(range(1, 13))
    qtd_dias = []
    
    for i in range(1, 13):
        dias_no_mes = calendar.monthrange(ano_farol, i)[1]
        qtd_dias.append(dias_no_mes)
    
    df_meses = pd.DataFrame({'Mes': meses, 'Qtd_dias': qtd_dias})

    df_dias_nao_conciliados = df_conciliacao_completa[df_conciliacao_completa['Data'].dt.year == ano_farol]
    df_dias_nao_conciliados = df_dias_nao_conciliados[df_dias_nao_conciliados['Conciliação'] != 0.0]
    df_dias_nao_conciliados['Data'] = df_dias_nao_conciliados['Data'].dt.month

    df_qtd_dias_nao_conciliados_mes = df_dias_nao_conciliados.groupby(['Data'])['Conciliação'].count().reset_index()
    df_qtd_dias_nao_conciliados_mes = df_qtd_dias_nao_conciliados_mes.merge(df_meses, left_on='Data', right_on='Mes', how='right')
    df_qtd_dias_nao_conciliados_mes['Porcentagem'] = df_qtd_dias_nao_conciliados_mes['Conciliação'] / df_qtd_dias_nao_conciliados_mes['Qtd_dias']
    df_qtd_dias_nao_conciliados_mes['Porcentagem'] = df_qtd_dias_nao_conciliados_mes['Porcentagem'].fillna(0)

    lista_dias_nao_conciliados = df_qtd_dias_nao_conciliados_mes['Porcentagem'].tolist()
    lista_dias_conciliados = []
    for dia in lista_dias_nao_conciliados:
        dia = round((1 - dia) * 100, 2)  # 2 casas decimais
        lista_dias_conciliados.append(dia)

    st.write(df_dias_nao_conciliados) # vou precisar
    st.write(df_qtd_dias_nao_conciliados_mes)
    mes_atual = datetime.now().month
    st.write(mes_atual)

    # Criar uma lista de dicionários com os valores e a cor para cada barra.
    dados_barras_com_cor = []
    for valor in lista_dias_conciliados:
        cor = '#008000' if valor == 100 else '#F1C61A'
        dados_barras_com_cor.append({
            "value": valor,
            "itemStyle": {
                "color": cor
            }
        })

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
            "type": 'value',
            "min": 0,
            "max": 100,
            "interval": 10,
            "axisLabel": {
            "formatter": '{value} %'
            }
            } 
        ],
        "series": [
            {
            "name": 'Total de Ajustes',
            "type": 'bar',
            "barWidth": "50%",
            "barGap": "5%",
            "data": dados_barras_com_cor,
            "itemStyle": {
                "color": "#F1C61A"
            },
            "label": {
                "show": True,
                "position": "insideTop",
            }
            },
            {
            "name": 'Ideal',
            "type": 'line',
            "yAxisIndex": 0,
            "data": [100,100,100,100,100,100,100,100,100,100,100,100]
            }
        ]
    }

    st_echarts(options=grafico_dias_conciliados, height="320px", width="100%")

    

