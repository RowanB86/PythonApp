# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 09:37:12 2025

@author: RowanBarua
"""

import streamlit as st
import pandas as pd
import numpy as np
import firebase_admin
from firebase_admin import credentials, initialize_app, db
import json
import openai
from funcs.functions import createAccount,logIn

if 'logged_in' not in st.session_state:
    st.session_state["logged_in"] == False

if st.session_state["logged_in"] == False:

    st.session_state['username'] = st.text_input("Enter your username:")
    st.session_state['password'] = st.text_input("Enter game password:",key='game_password1',type='password')
    
    create_account = st.button("Create account")
    login = st.button("Login")
    
    if create_account:
        result = createAccount(st.session_state['username'],st.session_state['password'])
        st.write(result)
    
    if login:
        result = logIn(st.session_state['username'],st.session_state['password'])
    
        if result = "Accepted":
            st.session_state["logged_in"] = True
        else:
            st.write("Username or password is not recognised.")
            st.session_state["logged_in"] = False
else:

    
