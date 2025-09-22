import streamlit as st
from streamlit.logger import get_logger
import pandas as pd
import os
import numpy as np
from datetime import datetime
from utils.queries import *
from utils.user import *
from utils.functions.general_functions import *


######## Config Pag ##########
st.set_page_config(
page_title="Conciliacao_FB",
page_icon="💰",
layout="centered",
initial_sidebar_state="collapsed"
)


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
    
    st.title(":moneybag: Conciliação Financeira - FB")
    st.write("")

    with st.container(border=True):
        userName = st.text_input(label="Login", value="", placeholder="Login", label_visibility="collapsed")
        userPassword = st.text_input(label="Senha", value="", placeholder="Senha",type="password", label_visibility="collapsed")
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            st.button("Login", use_container_width=True, on_click=handle_login, args=(userName, userPassword))

LOGGER = get_logger(__name__)


def main():

    if "loggedIn" not in st.session_state:
        st.session_state["loggedIn"] = False
        st.session_state["user_data"] = None

    if not st.session_state["loggedIn"]:
        show_login_page()
        st.stop()
    else: 
        st.switch_page("pages/Conciliações.py") 
        config_sidebar() # Personaliza menu lateral   


if __name__ == "__main__":
    main()


