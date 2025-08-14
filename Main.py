import streamlit as st
from streamlit.logger import get_logger
import pandas as pd
import os
import numpy as np
from datetime import datetime
from utils.queries import *
from utils.user import *
from utils.functions.general_functions import *
# from workalendar.america import Brazil
# import openpyxl

def handle_login(userName, userPassoword):
    users = st.secrets["users"]

    if userName not in users['emails']:
        st.error("Usuário sem permissão.")
        return
    
    if user_data := login(userName, userPassoword):
        st.session_state["loggedIn"] = True
        st.session_state["user_data"] = user_data
    else:
        st.session_state["loggedIn"] = False
        st.error("Email ou senha inválidos!")

def show_login_page():
    st.markdown(""" 
    <style>
        section[data-testid="stSidebar"][aria-expanded="true"]{
                display: none;
                }
    </style>
    """, unsafe_allow_html=True)
    
    st.title(":moneybag: DashBoard - Conciliação FB")
    st.write("")

    with st.container(border=True):
        userName = st.text_input(label="Login", value="", placeholder="Login", label_visibility="collapsed")
        userPassword = st.text_input(label="Senha", value="", placeholder="Senha",type="password", label_visibility="collapsed")
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            st.button("Login", use_container_width=True, on_click=handle_login, args=(userName, userPassword))

LOGGER = get_logger(__name__)


def run():
    ######## Puxando Dados #########
    conn_fb = mysql_connection_fb()
    
    @st.cache_data(show_spinner=False)
    def casas():
        result, column_names = execute_query(GET_CASAS, conn_fb)
        df_casas = pd.DataFrame(result, columns=column_names)   

        return df_casas
    st.session_state["df_casas"] = casas()

    @st.cache_data(show_spinner=False)
    def extrato_zig():
        result, column_names = execute_query(GET_EXTRATO_ZIG, conn_fb)
        df_extrato_zig = pd.DataFrame(result, columns=column_names)   

        df_extrato_zig['Data_Liquidacao'] = pd.to_datetime(df_extrato_zig['Data_Liquidacao']) 
        df_extrato_zig['Data_Transacao'] = pd.to_datetime(df_extrato_zig['Data_Transacao']) 

        return df_extrato_zig
    st.session_state["df_extrato_zig"] = extrato_zig()

    @st.cache_data(show_spinner=False)
    def zig_faturamento():
        result, column_names = execute_query(GET_ZIG_FATURAMENTO, conn_fb)
        df_zig_faturam = pd.DataFrame(result, columns=column_names)   

        df_zig_faturam['Data_Venda'] = pd.to_datetime(df_zig_faturam['Data_Venda']) 

        return df_zig_faturam
    st.session_state["df_zig_faturam"] = zig_faturamento()    

    @st.cache_data(show_spinner=False)
    def parcelas_receit_extr():
        result, column_names = execute_query(GET_PARCELAS_RECEITAS_EXTRAORDINARIAS, conn_fb)
        df_parc_receit_extr = pd.DataFrame(result, columns=column_names)   

        df_parc_receit_extr['Data_Ocorrencia'] = pd.to_datetime(df_parc_receit_extr['Data_Ocorrencia']) 
        df_parc_receit_extr['Vencimento_Parcela'] = pd.to_datetime(df_parc_receit_extr['Vencimento_Parcela'])
        df_parc_receit_extr['Recebimento_Parcela'] = pd.to_datetime(df_parc_receit_extr['Recebimento_Parcela'])

        return df_parc_receit_extr
    st.session_state["df_parc_receit_extr"] = parcelas_receit_extr()    

    @st.cache_data(show_spinner=False)
    def custos_blueme_sem_parcelam():
        result, column_names = execute_query(GET_CUSTOS_BLUEME_SEM_PARCELAMENTO, conn_fb)
        df_custos_blueme_sem_parcelam = pd.DataFrame(result, columns=column_names)   

        df_custos_blueme_sem_parcelam['Data_Vencimento'] = pd.to_datetime(df_custos_blueme_sem_parcelam['Data_Vencimento'], errors='coerce') 
        df_custos_blueme_sem_parcelam['Previsao_Pgto'] = pd.to_datetime(df_custos_blueme_sem_parcelam['Previsao_Pgto'], errors='coerce') 
        df_custos_blueme_sem_parcelam['Realizacao_Pgto'] = pd.to_datetime(df_custos_blueme_sem_parcelam['Realizacao_Pgto'], errors='coerce') 
        df_custos_blueme_sem_parcelam['Data_Competencia'] = pd.to_datetime(df_custos_blueme_sem_parcelam['Data_Competencia'], errors='coerce') 
        df_custos_blueme_sem_parcelam['Data_Lancamento'] = pd.to_datetime(df_custos_blueme_sem_parcelam['Data_Lancamento'], errors='coerce') 

        return df_custos_blueme_sem_parcelam
    st.session_state["df_custos_blueme_sem_parcelam"] = custos_blueme_sem_parcelam()  

    @st.cache_data(show_spinner=False)
    def custos_blueme_com_parcelam():
        result, column_names = execute_query(GET_CUSTOS_BLUEME_COM_PARCELAMENTO, conn_fb)
        df_custos_blueme_com_parcelam = pd.DataFrame(result, columns=column_names)   

        df_custos_blueme_com_parcelam['Vencimento_Parcela'] = pd.to_datetime(df_custos_blueme_com_parcelam['Vencimento_Parcela'], errors='coerce') 
        df_custos_blueme_com_parcelam['Previsao_Parcela'] = pd.to_datetime(df_custos_blueme_com_parcelam['Previsao_Parcela'], errors='coerce') 
        df_custos_blueme_com_parcelam['Realiz_Parcela'] = pd.to_datetime(df_custos_blueme_com_parcelam['Realiz_Parcela'], errors='coerce') 
        df_custos_blueme_com_parcelam['Data_Lancamento'] = pd.to_datetime(df_custos_blueme_com_parcelam['Data_Lancamento'], errors='coerce') 

        return df_custos_blueme_com_parcelam
    st.session_state["df_custos_blueme_com_parcelam"] = custos_blueme_com_parcelam()
    
    @st.cache_data(show_spinner=False)
    def extratos_bancarios():
        result, column_names = execute_query(GET_EXTRATOS_BANCARIOS, conn_fb)
        df_extratos_bancarios = pd.DataFrame(result, columns=column_names)   

        df_extratos_bancarios['Data_Transacao'] = pd.to_datetime(df_extratos_bancarios['Data_Transacao'], errors='coerce')

        return df_extratos_bancarios
    st.session_state["df_extratos_bancarios"] = extratos_bancarios()     

    @st.cache_data(show_spinner=False)
    def mutuos():
        result, column_names = execute_query(GET_MUTUOS, conn_fb)
        df_mutuos = pd.DataFrame(result, columns=column_names)   

        df_mutuos['Data_Mutuo'] = pd.to_datetime(df_mutuos['Data_Mutuo'], errors='coerce') 

        return df_mutuos
    st.session_state["df_mutuos"] = mutuos()         

    @st.cache_data(show_spinner=False)
    def tesouraria():
        result, column_names = execute_query(GET_TESOURARIA, conn_fb)
        df_tesouraria = pd.DataFrame(result, columns=column_names)   

        df_tesouraria['Data_Transacao'] = pd.to_datetime(df_tesouraria['Data_Transacao'], errors='coerce') 

        return df_tesouraria
    st.session_state["df_tesouraria"] = tesouraria()      

    @st.cache_data(show_spinner=False)
    def ajustes_conciliacao():
        result, column_names = execute_query(GET_AJUSTES_CONCILIACAO, conn_fb)
        df_ajustes_conciliacao = pd.DataFrame(result, columns=column_names)   

        df_ajustes_conciliacao['Data_Ajuste'] = pd.to_datetime(df_ajustes_conciliacao['Data_Ajuste'], errors='coerce') 

        return df_ajustes_conciliacao
    st.session_state["df_ajustes_conciliacao"] = ajustes_conciliacao()

    @st.cache_data(show_spinner=False)
    def bloqueios_judiciais():
        result, column_names = execute_query(GET_BLOQUEIOS_JUDICIAIS, conn_fb)
        df_bloqueios_judiciais = pd.DataFrame(result, columns=column_names)

        df_bloqueios_judiciais['Data_Transacao'] = pd.to_datetime(df_bloqueios_judiciais['Data_Transacao'], errors='coerce') 

        return df_bloqueios_judiciais
    st.session_state["df_bloqueios_judiciais"] = bloqueios_judiciais()  

    @st.cache_data(show_spinner=False)
    def tipo_class_cont_2():
        result, column_names = execute_query(GET_TIPO_CLASS_CONT_2, conn_fb)
        df_tipo_class_cont_2 = pd.DataFrame(result, columns=column_names)

        return df_tipo_class_cont_2
    st.session_state["df_tipo_class_cont_2"] = tipo_class_cont_2()

    @st.cache_data(show_spinner=False)
    def orcamentos():
        result, column_names = execute_query(GET_ORCAMENTOS, conn_fb)
        df_orcamentos = pd.DataFrame(result, columns=column_names)

        return df_orcamentos
    st.session_state["df_orcamentos"] = orcamentos()
    
    @st.cache_data(show_spinner=False)
    def faturamento_agregado():
        result, column_names = execute_query(GET_FATURAMENTO_AGREGADO, conn_fb)
        df_faturamento_agregado = pd.DataFrame(result, columns=column_names)

        return df_faturamento_agregado
    st.session_state["df_faturamento_agregado"] = faturamento_agregado()

    @st.cache_data(show_spinner=False)
    def eventos():
        result, column_names = execute_query(GET_EVENTOS, conn_fb)
        df_eventos = pd.DataFrame(result, columns=column_names)

        return df_eventos
    st.session_state["df_eventos"] = eventos()


def main():
    ######## Config Pag ##########
    st.set_page_config(
    page_title="Conciliacao_FB",
    page_icon="💰",
    )
    

    if "loggedIn" not in st.session_state:
        st.session_state["loggedIn"] = False
        st.session_state["user_data"] = None

    if not st.session_state["loggedIn"]:
        show_login_page()
        st.stop()
    else:
        run()  
        st.switch_page("pages/Conciliações.py") 
        # Personaliza menu lateral
        config_sidebar()     


if __name__ == "__main__":
    main()


