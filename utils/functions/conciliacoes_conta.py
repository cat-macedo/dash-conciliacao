import streamlit as st
import pandas as pd
from datetime import datetime
from utils.functions.general_functions import *
from utils.functions.conciliacoes import *
from utils.queries import *


def itens_por_conta(ids_outras, lista_ids, tab, df_custos_blueme_sem_parc, df_custos_blueme_com_parc, df_bloqueios, df_extratos_bancarios, conta, item):
    if conta == "Outras contas":
        # filtra os extratos
        df_extratos_outras = df_extratos_bancarios[df_extratos_bancarios['ID_Conta_Bancaria'].isin(ids_outras)]
        df_extratos_outras['Valor'] = df_extratos_outras['Valor'] * (-1)
        df_extratos_outras['Data_Transacao'] = df_extratos_outras['Data_Transacao'].dt.date

        if item == "blueme sem parcelamento":
            # filtra as despesas dessas contas
            df_blueme_outras = df_custos_blueme_sem_parc[
                df_custos_blueme_sem_parc['ID_Conta_Bancaria'].isin(ids_outras) 
                | df_custos_blueme_sem_parc['ID_Conta_Bancaria'].isna()]                
            df_blueme_outras['Realizacao_Pgto'] = df_blueme_outras['Realizacao_Pgto'].dt.date

            # faz o merge para tentar conciliar
            df_blueme_outras = df_blueme_outras.merge(
                df_extratos_outras,
                left_on=['Realizacao_Pgto', 'Valor'], 
                right_on=['Data_Transacao', 'Valor'],
                how='left'
            )

            # Seleciona só colunas mais importantes e reordena
            df_blueme_outras = df_blueme_outras[["ID_Despesa", "Fornecedor", "Valor", "Realizacao_Pgto", "Forma_Pagamento", "Class_Cont_1", "Class_Cont_2", "Doc_NF", "Status_Conf_Document", "Status_Aprov_Diret", "Status_Aprov_Caixa", "ID_Conta_Bancaria_x", "Conta_Bancaria", "ID_Extrato_Bancario", "Data_Transacao", "Descricao_Transacao"]]
            nova_ordem = ["ID_Conta_Bancaria_x", "Conta_Bancaria", "ID_Despesa", "Fornecedor", "Valor", "Realizacao_Pgto", "Forma_Pagamento", "Class_Cont_1", "Class_Cont_2", "Doc_NF", "Status_Conf_Document", "Status_Aprov_Diret", "Status_Aprov_Caixa", "ID_Extrato_Bancario", "Data_Transacao", "Descricao_Transacao"]
            df_blueme_outras = df_blueme_outras[nova_ordem]
            df_blueme_outras["ID_Conta_Bancaria_x"] = df_blueme_outras["ID_Conta_Bancaria_x"].astype("Int64")
            df_blueme_outras["ID_Extrato_Bancario"] = df_blueme_outras["ID_Extrato_Bancario"].astype("Int64")
            
            df_blueme_outras_styled = df_blueme_outras.style.apply(colorir_linhas(df_blueme_outras, 'ID_Despesa'), axis=1)
            st.dataframe(df_blueme_outras_styled, use_container_width=True, hide_index=True)

            # Estiliza e exibe 
            # df_blueme_outras_styled = df_blueme_outras.style.apply(colorir_consta_no_extrato, axis=1)
            # st.dataframe(df_blueme_outras_styled, use_container_width=True, hide_index=True)
            exibir_legenda("contas")
            st.divider()
        
        elif item == "blueme com parcelamento":
            # filtra as despesas dessas contas
            df_blueme_com_parc_outras = df_custos_blueme_com_parc[
                df_custos_blueme_com_parc['ID_Conta_Bancaria'].isin(ids_outras) 
                | df_custos_blueme_com_parc['ID_Conta_Bancaria'].isna()]                
            df_blueme_com_parc_outras['Realiz_Parcela'] = df_blueme_com_parc_outras['Realiz_Parcela'].dt.date

            # faz o merge para tentar conciliar
            df_blueme_com_parc_outras = df_blueme_com_parc_outras.merge(
                df_extratos_outras,
                left_on=['Realiz_Parcela', 'Valor_Parcela'], 
                right_on=['Data_Transacao', 'Valor'],
                how='left'
            )

            # Seleciona só colunas mais importantes e reordena
            df_blueme_com_parc_outras = df_blueme_com_parc_outras[["ID_Parcela", "ID_Despesa", "Fornecedor", "Qtd_Parcelas", "Num_Parcela", "Valor_Parcela", "Realiz_Parcela", "Forma_Pagamento", "Doc_NF", "Class_Cont_1", "Class_Cont_2", "Status_Conf_Document", "Status_Aprov_Diret", "Status_Aprov_Caixa", "ID_Conta_Bancaria_x", "Conta_Bancaria", "ID_Extrato_Bancario", "Data_Transacao", "Descricao_Transacao"]]
            nova_ordem = ["ID_Conta_Bancaria_x", "Conta_Bancaria", "ID_Parcela", "ID_Despesa", "Fornecedor", "Qtd_Parcelas", "Num_Parcela", "Valor_Parcela", "Realiz_Parcela", "Forma_Pagamento", "Doc_NF", "Class_Cont_1", "Class_Cont_2", "Status_Conf_Document", "Status_Aprov_Diret", "Status_Aprov_Caixa", "ID_Extrato_Bancario", "Data_Transacao", "Descricao_Transacao"]
            df_blueme_com_parc_outras = df_blueme_com_parc_outras[nova_ordem]
            df_blueme_com_parc_outras["ID_Conta_Bancaria_x"] = df_blueme_com_parc_outras["ID_Conta_Bancaria_x"].astype("Int64")
            df_blueme_com_parc_outras["ID_Extrato_Bancario"] = df_blueme_com_parc_outras["ID_Extrato_Bancario"].astype("Int64")

            df_blueme_com_parc_outras_styled = df_blueme_com_parc_outras.style.apply(colorir_linhas(df_blueme_com_parc_outras, 'ID_Parcela'), axis=1)
            st.dataframe(df_blueme_com_parc_outras_styled, use_container_width=True, hide_index=True)

            # Estiliza e exibe 
            # df_blueme_com_parc_outras_styled = df_blueme_com_parc_outras.style.apply(colorir_consta_no_extrato, axis=1)
            # st.dataframe(df_blueme_com_parc_outras_styled, use_container_width=True, hide_index=True)
            exibir_legenda("contas")
            st.divider()

    else:
        # filtra os extratos
        id_conta = lista_ids[tab]
        df_extratos_conta = df_extratos_bancarios[df_extratos_bancarios['ID_Conta_Bancaria'] == id_conta]
        df_extratos_conta['Valor'] = df_extratos_conta['Valor'] * (-1)
        df_extratos_conta['Data_Transacao'] = df_extratos_conta['Data_Transacao'].dt.date

        if item == "blueme sem parcelamento":
            # filtra as despesas dessas contas
            df_blueme_sem_parc_conta = df_custos_blueme_sem_parc[df_custos_blueme_sem_parc['ID_Conta_Bancaria'] == id_conta]
            df_blueme_sem_parc_conta['Realizacao_Pgto'] = df_blueme_sem_parc_conta['Realizacao_Pgto'].dt.date

            # faz o merge para tentar conciliar
            df_blueme_sem_parc = df_blueme_sem_parc_conta.merge(
                df_extratos_conta,
                left_on=['ID_Conta_Bancaria', 'Realizacao_Pgto', 'Valor'],
                right_on=['ID_Conta_Bancaria', 'Data_Transacao', 'Valor'],
                how='left'
            )

            # Seleciona só colunas mais importantes e reordena
            df_blueme_sem_parc = df_blueme_sem_parc[["ID_Despesa", "Fornecedor", "Valor", "Realizacao_Pgto", "Forma_Pagamento", "Class_Cont_1", "Class_Cont_2", "Doc_NF", "Status_Conf_Document", "Status_Aprov_Diret", "Status_Aprov_Caixa", "ID_Conta_Bancaria", "Conta_Bancaria", "ID_Extrato_Bancario", "Data_Transacao", "Descricao_Transacao"]]
            nova_ordem = ["ID_Conta_Bancaria", "Conta_Bancaria", "ID_Despesa", "Fornecedor", "Valor", "Realizacao_Pgto", "Forma_Pagamento", "Class_Cont_1", "Class_Cont_2", "Doc_NF", "Status_Conf_Document", "Status_Aprov_Diret", "Status_Aprov_Caixa", "ID_Extrato_Bancario", "Data_Transacao", "Descricao_Transacao"]
            df_blueme_sem_parc = df_blueme_sem_parc[nova_ordem]
            df_blueme_sem_parc["ID_Conta_Bancaria"] = df_blueme_sem_parc["ID_Conta_Bancaria"].astype("Int64")
            df_blueme_sem_parc["ID_Extrato_Bancario"] = df_blueme_sem_parc["ID_Extrato_Bancario"].astype("Int64")

            df_blueme_sem_parc_styled = df_blueme_sem_parc.style.apply(colorir_linhas(df_blueme_sem_parc, 'ID_Despesa'), axis=1)
            st.dataframe(df_blueme_sem_parc_styled, use_container_width=True, hide_index=True)

            # Estiliza a exibe
            # df_blueme_sem_parc_styled = df_blueme_sem_parc.style.apply(colorir_consta_no_extrato, axis=1)
            # st.dataframe(df_blueme_sem_parc_styled, use_container_width=True, hide_index=True)
            exibir_legenda("contas")
            st.divider()

        elif item == "blueme com parcelamento":
            # filtra as despesas dessas contas
            df_blueme_com_parc_conta = df_custos_blueme_com_parc[df_custos_blueme_com_parc['ID_Conta_Bancaria'] == id_conta]
            df_blueme_com_parc_conta['Realiz_Parcela'] = df_blueme_com_parc_conta['Realiz_Parcela'].dt.date

            # faz o merge para tentar conciliar
            df_blueme_com_parc = df_blueme_com_parc_conta.merge(
                df_extratos_conta,
                left_on=['ID_Conta_Bancaria', 'Realiz_Parcela', 'Valor_Parcela'],
                right_on=['ID_Conta_Bancaria', 'Data_Transacao', 'Valor'],
                how='left'
            )

            # Seleciona só colunas mais importantes e reordena
            df_blueme_com_parc = df_blueme_com_parc[["ID_Parcela", "ID_Despesa", "Fornecedor", "Qtd_Parcelas", "Num_Parcela", "Valor_Parcela", "Realiz_Parcela", "Forma_Pagamento", "Doc_NF", "Class_Cont_1", "Class_Cont_2", "Status_Conf_Document", "Status_Aprov_Diret", "Status_Aprov_Caixa", "ID_Conta_Bancaria", "Conta_Bancaria", "ID_Extrato_Bancario", "Data_Transacao", "Descricao_Transacao"]]
            nova_ordem = ["ID_Conta_Bancaria", "Conta_Bancaria", "ID_Parcela", "ID_Despesa", "Fornecedor", "Qtd_Parcelas", "Num_Parcela", "Valor_Parcela", "Realiz_Parcela", "Forma_Pagamento", "Doc_NF", "Class_Cont_1", "Class_Cont_2", "Status_Conf_Document", "Status_Aprov_Diret", "Status_Aprov_Caixa", "ID_Extrato_Bancario", "Data_Transacao", "Descricao_Transacao"]
            df_blueme_com_parc = df_blueme_com_parc[nova_ordem]
            df_blueme_com_parc["ID_Conta_Bancaria"] = df_blueme_com_parc["ID_Conta_Bancaria"].astype("Int64")
            df_blueme_com_parc["ID_Extrato_Bancario"] = df_blueme_com_parc["ID_Extrato_Bancario"].astype("Int64")
            
            # Em vez de eliminar duplicatas, vou sinalizar que não bateu só com um item do extrato
            # df_blueme_com_parc = df_blueme_com_parc.drop_duplicates(subset=["ID_Parcela"])
            df_blueme_com_parc_styled = df_blueme_com_parc.style.apply(colorir_linhas(df_blueme_com_parc, 'ID_Parcela'), axis=1)
            st.dataframe(df_blueme_com_parc_styled, use_container_width=True, hide_index=True)

            # Estiliza a exibe
            # df_blueme_com_parc_styled = df_blueme_com_parc.style.apply(colorir_consta_no_extrato, axis=1)
            # st.dataframe(df_blueme_com_parc_styled, use_container_width=True, hide_index=True)
            exibir_legenda("contas")
            st.divider()

        elif item == "bloqueios":
            # filtra as despesas dessas contas
            df_bloqueios_conta = df_bloqueios[df_bloqueios['ID_Conta_Bancaria'] == id_conta]                
            df_bloqueios_conta['Data_Transacao'] = df_bloqueios_conta['Data_Transacao'].dt.date
            df_bloqueios_conta['Valor'] = df_bloqueios_conta['Valor'] * (-1)

            # faz o merge para tentar conciliar
            df_bloqueios_conta = df_bloqueios_conta.merge(
                df_extratos_conta,
                left_on=['ID_Conta_Bancaria', 'Data_Transacao', 'Valor'], 
                right_on=['ID_Conta_Bancaria', 'Data_Transacao', 'Valor'],
                how='left'
            )

            # Seleciona só colunas mais importantes e reordena
            df_bloqueios_conta = df_bloqueios_conta[["ID_Bloqueio", "Data_Transacao", "ID_Conta_Bancaria", "Nome da Conta", "Valor", "Observacao",  "ID_Extrato_Bancario", "Descricao_Transacao"]]
            nova_ordem = ["ID_Conta_Bancaria", "Nome da Conta", "ID_Bloqueio", "Valor", "Data_Transacao", "Observacao",  "ID_Extrato_Bancario", "Descricao_Transacao"]
            df_bloqueios_conta = df_bloqueios_conta[nova_ordem]
            df_bloqueios_conta["ID_Conta_Bancaria"] = df_bloqueios_conta["ID_Conta_Bancaria"].astype("Int64")
            df_bloqueios_conta["ID_Extrato_Bancario"] = df_bloqueios_conta["ID_Extrato_Bancario"].astype("Int64")

            df_bloqueios_conta_styled = df_bloqueios_conta.style.apply(colorir_linhas(df_bloqueios_conta, 'ID_Bloqueio'), axis=1)
            st.dataframe(df_bloqueios_conta_styled, use_container_width=True, hide_index=True)

            # Estiliza e exibe 
            # df_bloqueios_conta_styled = df_bloqueios_conta.style.apply(colorir_consta_no_extrato, axis=1)
            # st.dataframe(df_bloqueios_conta_styled, use_container_width=True, hide_index=True)
            exibir_legenda("contas")
            st.divider()


# Cria uma tab para cada conta bancária da casa
def cria_tabs_contas(df_contas, id_casa, df_custos_blueme_sem_parc, df_custos_blueme_sem_parc_formatada, df_custos_blueme_com_parc, df_custos_blueme_com_parc_formatada, df_mutuos_formatada, df_bloqueios, df_extratos_bancarios, df_extratos_bancarios_formatada):
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

    # lista_contas = df_extratos_bancarios['Nome_Conta_Bancaria'].tolist()
    # Junta listas de várias bases
    lista_contas = (
        df_extratos_bancarios['Nome_Conta_Bancaria'].tolist()
        + df_custos_blueme_sem_parc['Conta_Bancaria'].tolist()
        + df_custos_blueme_com_parc['Conta_Bancaria'].tolist()
        + df_bloqueios['Nome da Conta'].tolist()
    )
    lista_contas = list(set(lista_contas))

    # cria tabs individuais só para os exclusivos
    for conta in lista_contas:
        # trata nulos como "Outras contas"
        if pd.isna(conta) or conta is None:
            if "Outras contas" not in lista_tabs:
                lista_tabs.append("Outras contas")
                lista_ids.append("OUTRAS")
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
        
    if lista_tabs:
        # garante que "Todas as contas" venha primeiro
        lista_tabs = ["Todas as contas"] + lista_tabs
        lista_ids = ["TODAS"] + lista_ids

        # garante que "Outras contas" fique por último
        if "Outras contas" in lista_tabs:
            idx = lista_tabs.index("Outras contas")
            lista_tabs.append(lista_tabs.pop(idx))
            lista_ids.append(lista_ids.pop(idx))
        
        # cria as tabs para cada conta
        tabs = st.tabs(lista_tabs)

        for tab, conta_fmt in enumerate(lista_tabs):
            with tabs[tab]:
                # st.subheader(conta_fmt)
                if conta_fmt == "Todas as contas":
                    exibe_tabelas_contas_a_pagar(
                        id_casa, 
                        df_custos_blueme_sem_parc_formatada, 
                        df_custos_blueme_com_parc_formatada, 
                        df_mutuos_formatada, 
                        df_bloqueios, 
                        df_extratos_bancarios_formatada)

                # Contas que não estão entre as principais da casa (tesouraria, petty cash, sem conta)
                elif conta_fmt == "Outras contas":
                    st.write("Petty cash, tesouraria, sem conta registrada, etc")

                    # pega os IDs que não são exclusivos
                    ids_outras = [
                            id_conta
                            for nome, id_conta in mapeamento_contas.items()
                            if id_conta not in ids_exclusivos
                        ]

                    # Despesas blueme sem parcelamento #
                    st.subheader('Despesas BlueMe Sem Parcelamento')
                    itens_por_conta(
                        ids_outras, 
                        lista_ids, tab, 
                        df_custos_blueme_sem_parc, 
                        df_custos_blueme_com_parc, 
                        df_bloqueios,
                        df_extratos_bancarios, 
                        conta_fmt, 
                        "blueme sem parcelamento")

                    # Despesas blueme com parcelamento #
                    st.subheader('Despesas BlueMe Com Parcelamento')
                    itens_por_conta(
                        ids_outras, 
                        lista_ids, 
                        tab, 
                        df_custos_blueme_sem_parc, 
                        df_custos_blueme_com_parc, 
                        df_bloqueios,
                        df_extratos_bancarios, 
                        conta_fmt, 
                        "blueme com parcelamento")
                    
                    # Saídas Mútuos #

                else:
                    # Despesas blueme sem parcelamento #
                    st.subheader('Despesas BlueMe Sem Parcelamento')
                    itens_por_conta(
                        None, 
                        lista_ids,
                        tab, 
                        df_custos_blueme_sem_parc, 
                        df_custos_blueme_com_parc,
                        df_bloqueios,
                        df_extratos_bancarios, 
                        conta_fmt, 
                        "blueme sem parcelamento"
                    )

                    # Despesas blueme com parcelamento #
                    st.subheader('Despesas BlueMe Com Parcelamento')
                    itens_por_conta(
                        None, 
                        lista_ids, 
                        tab, 
                        df_custos_blueme_sem_parc,
                        df_custos_blueme_com_parc, 
                        df_bloqueios,
                        df_extratos_bancarios, 
                        conta_fmt, 
                        "blueme com parcelamento"
                    )

                    # Bloqueos Judiciais #
                    st.subheader('Bloqueios Judiciais')
                    itens_por_conta(
                        None, 
                        lista_ids, 
                        tab, 
                        df_custos_blueme_sem_parc, 
                        df_custos_blueme_com_parc,
                        df_bloqueios, 
                        df_extratos_bancarios, 
                        conta_fmt, 
                        "bloqueios")
                    
                    # Saídas Mútuos #

    else: 
        st.warning('Nada para exibir')

# Exibe itens do CONTAS A PAGAR em TODAS AS CONTAS
def exibe_tabelas_contas_a_pagar(id_casa, df_custos_blueme_sem_parcelam_formatada, df_custos_blueme_com_parcelam_formatada, df_mutuos_formatada, df_bloqueios_judiciais_filtrada, df_extratos_bancarios_formatada):
    st.subheader("Despesas BlueMe Sem Parcelamento - Todas as contas")
    st.dataframe(df_custos_blueme_sem_parcelam_formatada, use_container_width=True, hide_index=True)
    st.divider()

    st.subheader("Despesas BlueMe Com Parcelamento - Todas as contas")
    st.dataframe(df_custos_blueme_com_parcelam_formatada, use_container_width=True, hide_index=True)
    st.divider()

    st.subheader("Saídas Mútuos - Todas as contas")
    df_mutuos_formatada = df_mutuos_formatada[df_mutuos_formatada['ID_Casa_Saida'] == id_casa]
    st.dataframe(df_mutuos_formatada, use_container_width=True, hide_index=True)
    st.divider()

    st.subheader("Bloqueios Judiciais - Todas as contas")
    df_bloqueios_judiciais_filtrada = df_bloqueios_judiciais_filtrada[df_bloqueios_judiciais_filtrada['Valor'] < 0]
    df_bloqueios_judiciais_formatada = formata_df(df_bloqueios_judiciais_filtrada)
    st.dataframe(df_bloqueios_judiciais_formatada, use_container_width=True, hide_index=True)
    st.divider()

    st.subheader("Extratos Bancários (Débito) - Todas as contas")
    df_extratos_bancarios_formatada = df_extratos_bancarios_formatada[df_extratos_bancarios_formatada['Tipo_Credito_Debito'] == 'DEBITO']
    st.dataframe(df_extratos_bancarios_formatada, use_container_width=True, hide_index=True)
    st.divider()

    # st.subheader("Contas Bancárias")
    # df_contas_filtrada = df_contas[df_contas['ID_Casa'] == id_casa]
    # st.dataframe(df_contas_filtrada, use_container_width=True, hide_index=True)
    # st.divider()
    # lista_contas_casa = df_contas_filtrada['Nome da Conta'].tolist()
