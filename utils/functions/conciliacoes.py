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


# Cria uma tab para cada conta bancária da casa
def cria_tabs_contas(lista_contas_casa, df_contas, id_casa, df_custos_blueme_sem_parc, df_extratos_bancarios):
    # Mapeamento nome → ID
    mapeamento_contas = dict(zip(df_contas["Nome da Conta"], df_contas["ID_Conta"]))

    # Lista de IDs que terão tabs individuais em cada casa
    ids_exclusivos_por_casa = {                      
        122: [113, 183],       
        114: [103, 130, 137],                        
        148: [148, 153, 164, 187],  
        173: [188, 190],                                             
        116: [140, 151],                           
        110: [117, 181],                          
        129: [109],                            
        127: [104, 176],             
        156: [145, 155, 168],    
        160: [154],    
        105: [105, 150, 160, 165],                         
        128: [115, 182],   
        104: [127, 138, 107, 110, 169],                         
        149: [132, 133, 134, 149],   
        115: [126, 139, 170, 186],
        142: [146],
        143: [111, 129],
        145: [124, 184, 185]                                              
    }

    # pega os exclusivos da casa atual (se existir)
    ids_exclusivos = ids_exclusivos_por_casa.get(id_casa, [])

    lista_tabs = []
    lista_ids = []

    lista_contas_custos_blueme = df_custos_blueme_sem_parc['Conta_Bancaria'].tolist()
    lista_contas_custos_blueme = list(set(lista_contas_custos_blueme))

    # cria tabs individuais só para os exclusivos
    for conta in lista_contas_custos_blueme:
        # ignora nulos
        if pd.isna(conta):
            continue  

        # pega o ID da conta de forma segura
        id_conta = mapeamento_contas.get(conta)

        if id_conta is None:
            # se não encontrar, joga pra "Outras contas"
            if "Outras contas" not in lista_tabs:
                lista_tabs.append("Outras contas")
                lista_ids.append("OUTRAS")
            continue

        if id_conta in ids_exclusivos:
            lista_tabs.append(conta)
            lista_ids.append(id_conta)
        else:
            if "Outras contas" not in lista_tabs:
                lista_tabs.append("Outras contas")
                lista_ids.append("OUTRAS")
        
    # cria as tabs no Streamlit
    tabs = st.tabs(lista_tabs)

    for i, conta_fmt in enumerate(lista_tabs):
        with tabs[i]:
            st.subheader(conta_fmt)

            # Contas que não estão entre as principais da casa (tesouraria, petty cash)
            if conta_fmt == "Outras contas":
                # pega os IDs que não são exclusivos
                ids_outras = [
                        id_conta
                        for nome, id_conta in mapeamento_contas.items()
                        if id_conta not in ids_exclusivos
                    ]

                # filtra as despesas dessas contas
                df_blueme_outras = df_custos_blueme_sem_parc[
                    df_custos_blueme_sem_parc['ID_Conta_Bancaria'].isin(ids_outras) 
                    | df_custos_blueme_sem_parc['ID_Conta_Bancaria'].isna()]                
                df_blueme_outras['Realizacao_Pgto'] = df_blueme_outras['Realizacao_Pgto'].dt.date

                # filtra também os extratos
                df_extratos_outras = df_extratos_bancarios[df_extratos_bancarios['ID_Conta_Bancaria'].isin(ids_outras)]
                df_extratos_outras['Valor'] = df_extratos_outras['Valor'] * (-1)
                df_extratos_outras['Data_Transacao'] = df_extratos_outras['Data_Transacao'].dt.date

                # faz o merge para tentar conciliar
                df_blueme_outras = df_blueme_outras.merge(
                    df_extratos_outras,
                    left_on=['Realizacao_Pgto', 'Valor'], # OLHAR ISSO AMANHA
                    right_on=['Data_Transacao', 'Valor'],
                    how='left'
                )

                st.dataframe(df_blueme_outras, use_container_width=True, hide_index=True)

            else:
                id_conta = lista_ids[i]
                st.write(f"Informações da conta **{conta_fmt}**")
                st.write(f"ID da conta: {id_conta}")

                # filtra as despesas dessas contas
                df_blueme_sem_parc_conta = df_custos_blueme_sem_parc[df_custos_blueme_sem_parc['ID_Conta_Bancaria'] == id_conta]
                df_blueme_sem_parc_conta['Realizacao_Pgto'] = df_blueme_sem_parc_conta['Realizacao_Pgto'].dt.date

                # filtra também os extratos
                df_extratos_conta = df_extratos_bancarios[df_extratos_bancarios['ID_Conta_Bancaria'] == id_conta]
                df_extratos_conta['Valor'] = df_extratos_conta['Valor'] * (-1)
                df_extratos_conta['Data_Transacao'] = df_extratos_conta['Data_Transacao'].dt.date

                # faz o merge para tentar conciliar
                df_blueme_sem_parc = df_blueme_sem_parc_conta.merge(
                    df_extratos_conta,
                    left_on=['ID_Conta_Bancaria', 'Realizacao_Pgto', 'Valor'],
                    right_on=['ID_Conta_Bancaria', 'Data_Transacao', 'Valor'],
                    how='left'
                )

                st.dataframe(df_blueme_sem_parc, use_container_width=True, hide_index=True)


# Função para conciliação geral inicial
def conciliacao_inicial(id_casa, casa, start_date, end_date, tab):
    ### Definindo Bases - Filtra por casa e data ###
    
    ## Extratos Zig
    df_extrato_zig = st.session_state["df_extrato_zig"]
    df_extrato_zig_filtrada, df_extrato_zig_formatada = filtra_formata_df(df_extrato_zig, "Data_Liquidacao", id_casa, start_date, end_date)
    
    ## Zig_Faturamento
    df_zig_faturam = st.session_state["df_zig_faturam"]
    df_zig_faturam_filtrada, df_zig_faturam_formatada= filtra_formata_df(df_zig_faturam, "Data_Venda", id_casa, start_date, end_date)

    ## Parcelas Receitas Extraordinarias
    df_parc_receit_extr = st.session_state["df_parc_receit_extr"]
    df_parc_receit_extr_filtrada, df_parc_receit_extr_formatada = filtra_formata_df(df_parc_receit_extr, "Recebimento_Parcela", id_casa, start_date, end_date)

    ## Custos BlueMe Sem Parcelamento
    df_custos_blueme_sem_parcelam = st.session_state["df_custos_blueme_sem_parcelam"]
    df_custos_blueme_sem_parcelam_filtrada, df_custos_blueme_sem_parcelam_formatada = filtra_formata_df(df_custos_blueme_sem_parcelam, "Realizacao_Pgto", id_casa, start_date, end_date)

    ## Custos BlueMe Com Parcelamento
    df_custos_blueme_com_parcelam = st.session_state["df_custos_blueme_com_parcelam"]
    df_custos_blueme_com_parcelam_filtrada, df_custos_blueme_com_parcelam_formatada = filtra_formata_df(df_custos_blueme_com_parcelam, "Realiz_Parcela", id_casa, start_date, end_date)
    
    ## Extratos Bancarios
    df_extratos_bancarios = st.session_state["df_extratos_bancarios"]
    df_extratos_bancarios_filtrada, df_extratos_bancarios_formatada = filtra_formata_df(df_extratos_bancarios, "Data_Transacao", id_casa, start_date, end_date)
    
    ## Mutuos
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
    
    ## Tesouraria
    df_tesouraria = st.session_state["df_tesouraria"]
    df_tesouraria_filtrada, df_tesouraria_formatada = filtra_formata_df(df_tesouraria, "Data_Transacao", id_casa, start_date, end_date)

    ## Ajustes Conciliação
    df_ajustes_conciliacao = st.session_state["df_ajustes_conciliacao"]
    df_ajustes_conciliacao_filtrada, df_ajustes_conciliacao_formatada = filtra_formata_df(df_ajustes_conciliacao, "Data_Ajuste", id_casa, start_date, end_date)

    ## Bloqueios Judiciais
    df_bloqueios_judiciais = st.session_state["df_bloqueios_judiciais"]
    df_bloqueios_judiciais_filtrada, df_bloqueios_judiciais_formatada = filtra_formata_df(df_bloqueios_judiciais, "Data_Transacao", id_casa, start_date, end_date)

    ## Eventos
    df_eventos = st.session_state["df_eventos"]
    df_eventos_filtrada, df_eventos_formatada = filtra_formata_df(df_eventos, "Recebimento Parcela", id_casa, start_date, end_date)

    ## Contas Bancárias
    df_contas = st.session_state["df_contas_bancarias"]


    if tab == 'Geral': # Exibe todos os dfs
        st.subheader("Extrato Zig")
        st.dataframe(df_extrato_zig_formatada, use_container_width=True, hide_index=True)
        st.divider()

        st.subheader("Zig Faturamento")
        st.dataframe(df_zig_faturam_formatada, use_container_width=True, hide_index=True)
        st.divider()

        st.subheader("Parcelas Receitas Extraordinárias")
        st.dataframe(df_parc_receit_extr_formatada, use_container_width=True, hide_index=True)
        st.divider()
        
        st.subheader("Despesas BlueMe Sem Parcelamento")
        st.dataframe(df_custos_blueme_sem_parcelam_formatada, use_container_width=True, hide_index=True)
        st.divider()

        st.subheader("Despesas BlueMe Com Parcelamento")
        st.dataframe(df_custos_blueme_com_parcelam_formatada, use_container_width=True, hide_index=True)
        st.divider()

        st.subheader("Extratos Bancários")
        st.dataframe(df_extratos_bancarios_formatada, use_container_width=True, hide_index=True)
        st.divider()

        st.subheader("Mútuos")
        st.dataframe(df_mutuos_formatada, use_container_width=True, hide_index=True)
        st.divider()

        st.subheader("Tesouraria")
        st.dataframe(df_tesouraria_formatada, use_container_width=True, hide_index=True)
        st.divider()

        st.subheader("Ajustes Conciliação")
        st.dataframe(df_ajustes_conciliacao_formatada, use_container_width=True, hide_index=True)
        st.divider()

        st.subheader("Bloqueios Judiciais")
        st.dataframe(df_bloqueios_judiciais_formatada, use_container_width=True, hide_index=True)
        st.divider()   

        st.subheader("Eventos")
        st.dataframe(df_eventos_formatada, use_container_width=True, hide_index=True)
        st.divider() 

        
        ## df de Conciliação
        st.subheader("Conciliação")

        # Criar um DataFrame com todas as datas do período selecionado
        df_conciliacao = pd.DataFrame()
        st.session_state['df_conciliacao'] = None

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

        # Eventos (desmembrar de Receitas Extraordinárias) #
        if 'Eventos' not in df_conciliacao.columns:
            df_conciliacao['Eventos'] = somar_por_data(
                df_eventos_filtrada, "Recebimento Parcela", "Valor Parcela", datas
            )

        # Entradas Mutuos #
        if 'Entradas Mútuos' not in df_conciliacao.columns:
            df_conciliacao['Entradas Mútuos'] = somar_por_data(
                df_mutuos_filtrada[df_mutuos_filtrada['ID_Casa_Entrada'] == id_casa], 
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
                df_mutuos_filtrada[df_mutuos_filtrada['ID_Casa_Saida'] == id_casa],
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

        # Estiliza linhas não conciliadas e exibe df de conciliação
        df_styled = df_formatado.style.apply(colorir_conciliacao, axis=1)
        st.dataframe(df_styled, use_container_width=True, hide_index=True)

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
    
    elif tab == 'Contas a Pagar':
        st.subheader("Despesas BlueMe Sem Parcelamento")
        st.dataframe(df_custos_blueme_sem_parcelam_formatada, use_container_width=True, hide_index=True)
        st.divider()

        st.subheader("Despesas BlueMe Com Parcelamento")
        st.dataframe(df_custos_blueme_com_parcelam_formatada, use_container_width=True, hide_index=True)
        st.divider()

        st.subheader("Saídas Mútuos")
        df_mutuos_formatada = df_mutuos_formatada[df_mutuos_formatada['ID_Casa_Saida'] == id_casa]
        st.dataframe(df_mutuos_formatada, use_container_width=True, hide_index=True)
        st.divider()

        st.subheader("Bloqueios Judiciais")
        df_bloqueios_judiciais_filtrada = df_bloqueios_judiciais_filtrada[df_bloqueios_judiciais_filtrada['Valor'] < 0]
        df_bloqueios_judiciais_formatada = formata_df(df_bloqueios_judiciais_filtrada)
        st.dataframe(df_bloqueios_judiciais_formatada, use_container_width=True, hide_index=True)
        st.divider()

        st.subheader("Extratos Bancários - Débito")
        df_extratos_bancarios_formatada = df_extratos_bancarios_formatada[df_extratos_bancarios_formatada['Tipo_Credito_Debito'] == 'DEBITO']
        st.dataframe(df_extratos_bancarios_formatada, use_container_width=True, hide_index=True)
        st.divider()

        st.subheader("Contas Bancárias")
        df_contas_filtrada = df_contas[df_contas['ID_Casa'] == id_casa]
        st.dataframe(df_contas_filtrada, use_container_width=True, hide_index=True)
        st.divider()
        lista_contas_casa = df_contas_filtrada['Nome da Conta'].tolist()
        
        cria_tabs_contas(lista_contas_casa, df_contas, id_casa, df_custos_blueme_sem_parcelam_filtrada, df_extratos_bancarios_filtrada)


# Cria tabela de conciliação para cada casa
def conciliacao_casa(df, casa, datas_completas):
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


