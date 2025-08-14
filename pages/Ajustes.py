import streamlit as st
import pandas as pd
from utils.functions.general_functions import *
from utils.queries import *


st.set_page_config(
    page_title="Conciliação FB - Ajustes",
    page_icon=":moneybag:",
    layout="wide"
)

# Se der refresh, volta para página de login
if 'loggedIn' not in st.session_state or not st.session_state['loggedIn']:
	st.switch_page('Main.py')

# Personaliza menu lateral
config_sidebar()

st.title(":moneybag: Ajustes")
st.divider()
