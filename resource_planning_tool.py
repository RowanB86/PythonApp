from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import pandas as pd
import streamlit as st
import numpy as np
import firebase_admin
from firebase_admin import credentials, initialize_app, db
import json
import openai


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
    
    with st.sidebar.expander("Add Team Member"):
        first_name = st.text_input("First Name:")
        last_name = st.text_input("Last Name:")
        select_grade = st.selectbox("Select Grade",options=['D1','D2','D3','D4','D5','D6','D7'])
        primary_skill = st.text_input("Primary Capability:")
        secondary_skill = st.text_input("Secondary Capability:")
        
        add_team_member = st.button("Add Team Member")
        
        if add_team_member:
            ref = db.reference("Team Members")
            new_team_member = {"FirstName": first_name, "LastName": last_name, "Grade": select_grade, "PrimarySkill": primary_skill, "SecondarySkill": secondary_skill}
            ref.push(new_team_member)
            st.write("Team member added.")
            
        
    with st.sidebar.expander("Add Opportunity"):
        project_name = st.text_input("Enter Project Name:")
        on_contract = st.selectbox("Set Contract Status",options=['On Contract','Not On Contract'])
        
        add_opportunity = st.button("Add Opportunity")
        
        if add_opportunity:
            ref = db.reference("projects")
            
            if ref:
                opportunities = ref.get()
                opportunity_exists = False
                
                for opportunity_id,opportunity in opportunities.items():
                    if opportunity["Project"] == project_name:
                        opportunity_exists = True
                        break
            
            
            if opportunity_exists:
                st.write("An opportunity with this name already exists.")
            else:
                new_project = {"Project": project_name, "Status": on_contract}
                ref.push(new_project)
                st.write("New opportunity added.")        
                
    with st.sidebar.expander("Assign Team Member to Opportunity"):
        
        ref = db.reference("projects")
        
        if ref:
            opportunities = ref.get()
            opportunity_list = []
            
            for opportunity_id,opportunity in opportunities.items():
                opportunity_list.append(opportunity["Project"])
            
            

    
    #with st.expander("Create new game"):
    # Sample data for schedule
    data = {
        "Team Member": ["Alice", "Bob", "Charlie"],
        "Monday": ["Project A", "Project B", "Off"],
        "Tuesday": ["Project A", "Project C", "Project B"],
        "Wednesday": ["Off", "Project A", "Project C"],
        "Thursday": ["Project B", "Project A", "Off"],
        "Friday": ["Project C", "Off", "Project A"],
    }
    df = pd.DataFrame(data)
    
    # Custom JS for cell color
    cell_style = JsCode("""
    function(params) {
        if (params.value === "Off") {
            return { 'backgroundColor': 'lightgray', 'color': 'black' };
        } else if (params.value.includes("Project A")) {
            return { 'backgroundColor': 'lightblue', 'color': 'black' };
        }
        return null;
    }
    """)
    
    # Grid options
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=True, cellStyle=cell_style)
    gb.configure_grid_options(domLayout='autoHeight')
    grid_options = gb.build()
    
    # Display editable grid with unsafe JS code enabled
    st.set_page_config(layout="wide")  # Wider view for Streamlit
    st.write("Editable Weekly Schedule")
    AgGrid(df, gridOptions=grid_options, height=400, width='100%', allow_unsafe_jscode=True)
