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
import textwrap
from streamlit_ace import st_ace
from funcs.functions import createAccount,logIn,convertToDataFrame,save_dataframe_to_firebase,load_dataframe,SQLTransform

if "reset_input" not in st.session_state:
    st.session_state["reset_input"] = False  # ✅ Flag to track reset

if 'logged_in' not in st.session_state:
    st.session_state["logged_in"] = False

if 'page_selection' not in st.session_state:
    st.session_state["page_selection"] = ''

if 'login_result' not in st.session_state:
    st.session_state["login_result"] = ''

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

if 'sql_code' not in st.session_state:
    st.session_state["sql_code"] = textwrap.dedent("""

    --Write your SQL code below. Use the dataset names as table names.:

    SELECT * 
    FROM
    Table_Name
    
    
    """)
    
def clear_text(delete_acknowledgement,selected_dataset):
    if st.session_state["user_input"] == "I want to delete this table.":
        ref = db.reference(selected_dataset)
        ref.delete()
        ref = db.reference("Datasets")
        datasets = ref.order_by_child("dataset").equal_to(selected_dataset).get() 
    
        if datasets is not None:
            for dataset_id,dataset in datasets.items():
                datasetID = dataset_id
    
            ref = db.reference(f"Datasets/{datasetID}")
            ref.delete()

        st.session_state["reset_input"] = True 
        st.rerun()
        
if st.session_state["logged_in"] == False:

    st.session_state['username'] = st.text_input("Enter your username:")
    st.session_state['password'] = st.text_input("Enter game password:",key='game_password1',type='password')
    
    create_account = st.button("Create account")
    login = st.button("Login")

    st.write(st.session_state["login_result"])
    
    if create_account:
        result = createAccount(st.session_state['username'],st.session_state['password'])
    
    if login:
        result = logIn(st.session_state['username'],st.session_state['password'])
    
        if result == "Accepted":
            st.session_state["logged_in"] = True
        else:
            st.session_state["login_result"] = "Username or password is not recognised."
            st.session_state["logged_in"] = False
        
        st.rerun()
else:

    with st.sidebar:
        st.session_state["page_selection"] = st.selectbox("Select page",options=["Create New Dataset","Transform Datasets"])
            
    if st.session_state["page_selection"] == "Create New Dataset":
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
                            st.rerun()
                            
        with st.expander("Datasets"):
            ref = db.reference("Datasets")
            datasets = ref.get()
            dataset_list = []

            if datasets is not None:
                for dataset_id,dataset in datasets.items():
                    dataset_list.append(dataset["dataset"])

            dataset_list = sorted(dataset_list)

            selected_dataset = st.selectbox("Select dataset",options=dataset_list)

            df = load_dataframe(selected_dataset)
            st.dataframe(df)

            if st.session_state["reset_input"]:
                st.session_state["user_input"] = ""  # Reset input field
                st.session_state["reset_input"] = False  # ✅ Reset flag
                st.rerun()  # ✅ Force one more rerun to clear input properly
            
            delete_acknowledgement = st.text_input("To delete this table, enter \"I want to delete this table.\" and press the \"Delete Table\" button.",
            key="user_input")
            st.button("Delete table",on_click=clear_text,args=(delete_acknowledgement, selected_dataset))

    elif st.session_state["page_selection"] == "Transform Datasets":

        with st.expander("Datasets"):
            ref = db.reference("Datasets")
            datasets = ref.get()
            dataset_list = []

            if datasets is not None:
                for dataset_id,dataset in datasets.items():
                    dataset_list.append(dataset["dataset"])

            dataset_list = sorted(dataset_list)

            selected_dataset = st.selectbox("Select dataset",options=dataset_list)

            df = load_dataframe(selected_dataset)
            st.dataframe(df)    

        with st.expander("Transform datasets using SQLite"):
            updated_code = st_ace(value=st.session_state['sql_code'], language='sql', theme='monokai', key='ace-editor')

            perform_transform = st.button("Perform_Transform")

            if perform_transform:
            
                if updated_code != st.session_state['sql_code']:
                    st.session_state['sql_code'] = updated_code
                    
                code = SQLTransform(st.session_state['sql_code'])
                st_ace(value=code, language='sql', theme='monokai', key='ace-editor2')
                local_namespace = {}
                exec(code,{},local_namespace)
                df = local_namespace.get("df")
                st.dataframe(df)
                st.rerun()
                
