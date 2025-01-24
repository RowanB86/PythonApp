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
from funcs.functions import createAccount,logIn,convertToDataFrame

if 'logged_in' not in st.session_state:
    st.session_state["logged_in"] = False

if 'page_selection' not in st.session_state:
    st.session_state["page_selection"] = ''

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
    
        if result == "Accepted":
            st.session_state["logged_in"] = True
        else:
            st.write("Username or password is not recognised.")
            st.session_state["logged_in"] = False

        st.rerun()
else:

    with st.sidebar:
        st.session_state["page_selection"] = st.selectbox("Select page",options=["Create new dataset"])
        
    if st.session_state["page_selection"] == "Create new dataset":
        with st.expander("Upload local file"):
            Dataset_Upload = st.file_uploader("Upload dataset", type=["xlsx","xls","xlsm",'csv'])

            if Dataset_Upload is not None:
                file_type = Dataset_Upload.name.split(".")[-1] 
                dataframe_created = False
    
                if file_type == "csv":
                    df = convertToDataFrame(Dataset_Upload)
                    st.dataframe(df)
                    dataframe_created = True
                    
                else:
                    sheet_names = convertToDataFrame(uploaded_file)
                    sheet_name = st.selectbox("Select sheet",options=sheet_names)
                    create_dataframe = st.button("Create Dataframe")
    
                    if create_dataframe:
                        df = pd.read_excel(excel_file, sheet_name=selected_sheet)
                        st.dataframe(df)
                        dataframe_created = True

                if dataframe_created:
                    df_name = st.text_input("Enter dataframe name:")
                    save_df = st.button("Save dataframe")
                    if save_df:
                        if len(df_name) == 0:
                            st.write("Please enter a name for the dataframe.")
                        else:
                            result = save_dataframe_to_firebase(df, df_name)
                            st.write(result)
