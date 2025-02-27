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
import duckdb
from streamlit_ace import st_ace
from funcs.functions import createAccount,logIn,convertToDataFrame,save_dataframe_to_firebase,load_dataframe,SQLTransform,DuckDBTransform

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

if "transform_created" not in st.session_state:
    st.session_state["transform_created"] = False

if "save_transform_result" not in st.session_state:
    st.session_state["save_transform_result"] = ''

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
        st.session_state["page_selection"] = st.selectbox("Select page",options=["Create / Delete Datasets","Transform Datasets","Statistical Modelling"])
            
    if st.session_state["page_selection"] == "Create / Delete Datasets":
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
                            result = save_dataframe_to_firebase(df, df_name,False)
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
        
        with st.expander("Transform datasets using PostgreSQL"):
            updated_code = st_ace(value=st.session_state['sql_code'], language='sql', theme='monokai', key='ace-editor')

            if st.button("Perform_Transform"):
                
                st.session_state["save_transform_result"] = ''
                
                if updated_code != st.session_state['sql_code']:
                    st.session_state['sql_code'] = updated_code

                try:
                    
                    local_namespace = {}
                    code = DuckDBTransform(st.session_state['sql_code'])
                    exec(code,{},local_namespace)
                    st.session_state["df_transform"] = local_namespace.get("df")
                    
                    st.session_state["transform_created"] = True
                    st.session_state["save_transform_result"] = ''
      
                except duckdb.Error as e:
                    st.error(f"SQL Execution Error: {str(e)}")  
                except Exception as e:
                    st.error(f"Unexpected Error: {str(e)}")      

            if 'df_transform' in st.session_state:
                st.dataframe(st.session_state["df_transform"])

            if st.session_state["transform_created"]:
                allow_overwrite = st.radio("Allow dataset overwrites.",["Yes","No"],index=1)
                df_name = st.text_input("Enter dataset name:")

                if st.button("Save dataset"):
                    if 'df_transform' not in st.session_state:
                        st.session_state["save_transform_result"] = "No dataset has been created."
                    else:
                        st.session_state["save_transform_result"] = save_dataframe_to_firebase(st.session_state["df_transform"], df_name,allow_overwrite)
                        st.session_state["transform_created"] = False
                        st.rerun()

            transform_result = st.empty()
            transform_result.text(st.session_state["save_transform_result"])
    
    elif st.session_state["page_selection"] == "Statistical Modelling":  

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

        with st.expander("Define and fit model using statsmodel syntax e.g. 'SalesPrice ~ LotArea + OverallQual + OverallCond'"):
            st.markdown("""**Model Definition Guidelines:**
            A model should be defined in the form; Target_Variable ~ Feature1 + Feature2 + Feature3
            Example: SalePrice ~ LotArea + OverallQual + OverallCond

            Target_Variable = The thing that you're trying to predict.
            Feature1, Feature2, ...  = The factors (explanatory variables) that affect the target variable (e.g. number of bedrooms in a house can affect the sales price).""")
            
        with st.expander("Define and fit model interactively"):
            selected_dataset = st.selectbox("Select dataset to fit model to",options=dataset_list)
            df = load_dataframe(selected_dataset)   
            variables = list(df.columns)
            if 'interaction_terms' not in st.session_state:
                st.session_state["interaction_terms"] = []
                st.session_state["interaction_term_update_message"] = ''

            if 'higher_order_terms' not in st.session_state:
                st.session_state["higher_order_terms"] = []
                st.session_state["higher_order_term_update_message"] = ''
            
            target_variable = st.selectbox("Select target variable (what you're trying to predict)",options=variables)
            explanatory_variables = st.selectbox("Select explanatory variables (the variables you think affect the target variable)",options=variables + st.session_state["interaction_terms"] + st.session_state["higher_order_terms"])

            st.markdown("""**Create interaction terms**""")
            interaction_term = st.multiselect("Select explanatory variables to combine to create interaction terms",options=variables)
            if st.button("Create interaction term"):
                new_interaction_term = ('*').join(interaction_term)
                if new_interaction_term not in st.session_state["interaction_terms"]:
                    st.session_state["interaction_terms"].append(new_interaction_term)
                    st.session_state["interaction_term_update_message"] = 'Interaction term; ' + new_interaction_term + ' has been created.'
                else:
                    st.session_state["interaction_term_update_message"] = 'Interaction term; ' + new_interaction_term + ' already exists.'

                st.rerun()

            if "interaction_term_update_message" in st.session_state:
                st.success(st.session_state["interaction_term_update_message"])

            st.markdown("""**Create higher order terms**""")
            higher_order_term =  st.selectbox("Select variable",options=variables)
            order_of_term = st.text_input("Enter power to raise term by e.g. 2 = squared term, 3 = cubic term")

            if order_of_term is not None:
                try:
                    order_of_term = int(order_of_term)
                except:
                    st.write("Please enter numeric value for order of term.")
            
            if st.button("Create higher order term"):
                new_higher_order_term = 'I(' + higher_order_term + '^' + str(order_of_term) + ')'
                if new_higher_order_term not in st.session_state["higher_order_terms"]:
                    st.session_state["higher_order_terms"].append(new_higher_order_term)
                    st.session_state["higher_order_term_update_message"]  = 'Higher order term; ' + new_higher_order_term + ' has been created.'
                else:
                    st.session_state["higher_order_term_update_message"]  = 'Higher order term; ' + new_higher_order_term + ' already exists.'

                st.rerun()
        
            if "higher_order_term_update_message" in st.session_state:
                st.success(st.session_state["higher_order_term_update_message"])           
            
