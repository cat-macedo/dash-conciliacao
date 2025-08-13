import streamlit as st
import requests

def login(userName: str, userPassword: str) -> bool:
    if (userName is None):
        return False
    
    login_data = {
        "username": userName,
        "password": userPassword,
        "loginSource": 1,
    }

    login = requests.post('https://apps.blueprojects.com.br/fb/Security/Login',json=login_data).json()

    if "error" in login:
        return False
    else:
        if login["data"]["success"] == True:
            return login
        else:
            return False
    
def logout():
    st.cache_data.clear()
    st.session_state = {}