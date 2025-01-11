
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import pandas as pd
import streamlit as st
import numpy as np
import firebase_admin
from firebase_admin import credentials, initialize_app, db
import json
import openai
#st.set_page_config(layout="wide")  # Wider view for Streamlit
firebase_credentials = json.loads(st.secrets["firebase"]["service_account_json"])

if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(firebase_credentials)
        initialize_app(cred, {
            'databaseURL': 'https://resourceplanning-f5a14-default-rtdb.europe-west1.firebasedatabase.app'
        })
        st.write("Firebase initialized successfully.")
    except Exception as e:
        st.error(f"Error initializing Firebase: {e}")


if 'logged_in' not in st.session_state:
    st.session_state["logged_in"] = False
    

if not st.session_state["logged_in"]:

    st.session_state['username'] = st.text_input("Enter your username:")
    st.session_state['password']  = st.text_input("Enter game password:",key='game_password1',type='password')
    
    create_account = st.button("Create Account")
    log_in = st.button("Log In")

    if create_account:
        ref = db.reference("accounts")
        if ref:
            account_exists = False
            
        accounts = ref.get()

        if accounts is not None:
            for account_id,account_data in accounts.items():
                if account_data["username"] == st.session_state['username']:
                    account_exists = True 
                    break
                
        if account_exists:
            st.write(f"Account with username; {st.session_state['username']} already exists.")
        else:
            new_account = {"username": st.session_state['username'], "password": st.session_state['password']}
            ref.push(new_account) 
            st.write("New account created.")
    
    if log_in:
        ref = db.reference("accounts")
        
        if ref:
            access_granted = False
            try:
                ref = db.reference("accounts")
                accounts = ref.get()
                st.write("Accounts:", accounts)
            except Exception as e:
                st.error(f"Error: {e}")

            for account_id,account_data in accounts.items():
                if account_data["username"] == st.session_state['username'] and account_data["password"] == st.session_state['password']:
                    access_granted = True 
                    break
                    
            if access_granted:
                st.session_state["logged_in"]= True
                st.rerun()
            else:
                st.write("Username or password is incorrect.")
                       
else:
    

        
        
    
    # Sample data for schedule
    if "grid_data" not in st.session_state:
        st.session_state["grid_data"] = {
            "Team Member": ["Alice", "Bob", "Charlie"],
            "Monday": ["Project A", "Project B", "Off"],
            "Tuesday": ["Project A", "Project C", "Project B"],
            "Wednesday": ["Off", "Project A", "Project C"],
            "Thursday": ["Project B", "Project A", "Off"],
            "Friday": ["Project C", "Off", "Project A"],
        }
    
    # Use session state data
    df = pd.DataFrame(st.session_state["grid_data"])

    st.write("DataFrame Preview:")
    st.write(df)  # Ensure DataFrame displays correctly
    
    # Grid options
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=True)  # Simplified setup
    grid_options = gb.build()
    
    # Display editable grid
    st.write("Editable Weekly Schedule")
    AgGrid(df, gridOptions=grid_options)
