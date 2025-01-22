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


firebase_credentials = json.loads(st.secrets["firebase"]["service_account_json"])
cred = credentials.Certificate(firebase_credentials)

if not firebase_admin._apps:
    # Initialize Firebase
    initialize_app(cred, {
        'databaseURL': 'https://data-science-d6833-default-rtdb.europe-west1.firebasedatabase.app/'
    })
    

st.session_state['username'] = st.text_input("Enter your username:")
st.session_state['password'] = st.text_input("Enter game password:",key='game_password1',type='password')


create_account = st.button("Create account")
login = st.button("Login")

if create_account:
    ref = db.reference("accounts")
    new_account = {"username": st.session_state['username'], "password": st.session_state['password']}
    ref.push(new_account)