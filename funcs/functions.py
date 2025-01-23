# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 10:18:09 2025

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
    
    
def createAccount(username,password):
    ref = db.reference("accounts")
    accounts = ref.get()
    account_exists = False

    if accounts is not None:
        for account_id,account in accounts.items():
            if st.session_state['username'] == account["username"]: 
                account_exists = True
    
    if account_exists:
        result = f"An account with the username; {st.session_state['username']} already exists."
    else:
        new_account = {"username": st.session_state['username'], "password": st.session_state['password']}
        ref.push(new_account)
        result = "Account created."
    
    return result

def logIn(username,password):
    ref = db.reference("accounts")
    accounts = ref.get()
    verified = False

    if accounts is not None:
        for account_id,account in accounts.items():
            if st.session_state['username'] == account["username"] and st.session_state['password'] == account["password"]: 
                verified = True
    
    if verified:
        result = "Accepted"
    else:
        result = "Denied"
    
    return result

def convertToDataFrame(file):
    file_type = file.name.split(".")[-1]

    if file_type == "csv":
        df = pd.read_csv(file)  
        return df
        
    else:
        excel_file = pd.ExcelFile(file) 
        sheet_names = excel_file.sheet_names

        return sheet_names
