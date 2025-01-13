
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import pandas as pd
import streamlit as st
import numpy as np
import firebase_admin
from firebase_admin import credentials, initialize_app, db
import json
import openai
import plotly.graph_objects as go
from dash import Dash, dash_table
import streamlit.components.v1 as components

st.set_page_config(layout="wide")  # Wider view for Streamlit

firebase_credentials = json.loads(st.secrets["firebase"]["service_account_json"])

def dataframe_to_frozen_html_table(df):
    html_table = """
    <style>
    .table-container {
        overflow-x: auto;
        white-space: nowrap;
        position: relative;
    }
    .frozen-table {
        border-collapse: collapse;
        table-layout: auto;
        width: 100%;
    }
    .frozen-table th, .frozen-table td {
        border: 1px solid black;
        padding: 5px;
        text-align: center;
    }
    .frozen-table th {
        background-color: #003366;
        color: white;
        position: sticky;
        top: 0;
        z-index: 2;
    }
    .frozen-table th.frozen {
        background-color: black; /* Black background for the first three headers */
        color: white; /* White text for contrast */
        font-weight: bold; /* Bold text for better visibility */
        z-index: 3;
    }
    .frozen-table td.frozen {
        background-color: #f2f2f2;
        z-index: 1;
    }
    /* Freeze the first three columns */
    .frozen-table th:nth-child(1),
    .frozen-table th:nth-child(2),
    .frozen-table th:nth-child(3),
    .frozen-table td:nth-child(1),
    .frozen-table td:nth-child(2),
    .frozen-table td:nth-child(3) {
        position: sticky;
        left: 0;
    }
    .frozen-table th:nth-child(2) {
        left: 80px; /* Adjust for first column width */
    }
    .frozen-table th:nth-child(3) {
        left: 160px; /* Adjust for first two column widths */
    }
    .frozen-table td:nth-child(2) {
        left: 80px; /* Adjust for first column width */
    }
    .frozen-table td:nth-child(3) {
        left: 160px; /* Adjust for first two column widths */
    }
    </style>
    <div class="table-container">
        <table class="frozen-table">
            <thead>
                <tr>
    """
    # Add column headers with specific classes for the first three columns
    for i, col in enumerate(df.columns):
        if i < 3:  # First three columns
            html_table += f"<th class='frozen'>{col}</th>"
        else:
            html_table += f"<th>{col}</th>"
    html_table += "</tr></thead><tbody>"

    # Add table rows with specific classes for the first three columns
    for _, row in df.iterrows():
        html_table += "<tr>"
        for i, cell in enumerate(row):
            if i < 3:  # First three columns
                html_table += f"<td class='frozen'>{cell}</td>"
            else:
                html_table += f"<td>{cell}</td>"
        html_table += "</tr>"
    html_table += "</tbody></table></div>"
    return html_table


if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(firebase_credentials)
        initialize_app(cred, {
            'databaseURL': 'https://resourceplanning-f5a14-default-rtdb.europe-west1.firebasedatabase.app'
        })

    except Exception as e:
        st.error(f"Error initializing Firebase: {e}")


if 'logged_in' not in st.session_state:
    st.session_state["logged_in"] = False
    

if not st.session_state["logged_in"]:

    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
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
            ref = db.reference("team_members")
            new_team_member = {"first_name": first_name, "last_name": last_name, "grade": select_grade, "primary_skill": primary_skill, "secondary_skill": secondary_skill}
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

                if opportunities is not None:
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

            if opportunities is not None:
            
                for opportunity_id,opportunity in opportunities.items():
                    opportunity_list.append(opportunity["Project"])

        ref = db.reference("team_members")
        
        if ref:
            team_members = ref.get()
            team_list = []
            row = 1

            if team_members is not None:
                for employee_id,employee in team_members.items():
                    team_list.append(employee["first_name"] + ' ' +  employee["last_name"] + ' (' + str(row) + ')')
                    row += 1

        project = st.selectbox("Select opportunity",options=opportunity_list)
        employee = st.selectbox("Select team member to assign to opportunity",options=team_list)
        capability = st.text_input("Primary capability that team member will fulfil:")
        start_date = st.text_input("Opportunity start date (dd/mm/yyyy):")
        end_date = st.text_input("Opportunity end date (dd/mm/yyyy):")
        st.markdown("<b>Working Hours:</b>", unsafe_allow_html=True)   
        monday = st.text_input("Monday:")
        tuesday = st.text_input("Tuesday:")
        wednesday = st.text_input("Wednesday:")
        thursday = st.text_input("Thursday:")
        friday = st.text_input("Friday:")

        assign_to_project = st.button("Assign team member to opportunity.")

        if assign_to_project:
            if pd.to_datetime(end_date, format='%d/%m/%Y') <= pd.to_datetime(start_date, format='%d/%m/%Y'):
                st.write("End date should be later than start date")
            else:
                
                new_entry = {"project": project, "capability": capability, "employee": employee, "start_date": start_date, \
                             "end_date": end_date, "monday": monday, "tuesday": tuesday, "wednesday": wednesday, "thursday": thursday, \
                            "friday": friday}
    
                ref = db.reference("schedule")
                ref.push(new_entry)

    with st.sidebar.expander("Team Members"):
        ref = db.reference("team_members")
        df = pd.DataFrame(columns=["Employee_ID","First_Name","Last_Name","Grade","Primary_Capability","Secondary_Capability"])

        if ref:
            employees = ref.get()

            if employees is not None:
                for employee_ID, employee in employees.items():
                    next_row = len(df)
                    df.loc[next_row] = [None]*len(df.columns)
                    df.iloc[next_row,0] = employee_ID
                    df.iloc[next_row,1] = employee["first_name"]
                    df.iloc[next_row,2] = employee["last_name"]
                    df.iloc[next_row,3] = employee["grade"]
                    df.iloc[next_row,4] = employee["primary_skill"]
                    df.iloc[next_row,5] = employee["secondary_skill"]
                    
             # Generate an HTML table without the index
            html_table = df.to_html(index=False)
            
            # Display the table in Streamlit
            st.markdown(html_table, unsafe_allow_html=True)       
            
    container = st.container()

    with container:
          # Use CSS to make the table container wider
        st.markdown(
            """
            <style>
            .schedule-container {
                width: 100%; /* Full width for the schedule */
                margin: 0 auto;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )      
        data = {
            "Team Member": ["Alice", "Bob", "Charlie"],
            "Monday": ["Project A", "Project B", "Off"],
            "Tuesday": ["Project A", "Project C", "Project B"],
            "Wednesday": ["Off", "Project A", "Project C"],
            "Thursday": ["Project B", "Project A", "Off"],
            "Friday": ["Project C", "Off", "Project A"],
        }

        ref = db.reference("schedule")

        if ref:
            entries = ref.get()

            if entries is not None:
                row = 0
                for entry_id,entry in entries.items():
                    if row == 0:
                        min_start_date = pd.to_datetime(entry["start_date"],format = '%d/%m/%Y')
                        max_end_date = pd.to_datetime(entry["end_date"],format = '%d/%m/%Y')
                    else:
                        if pd.to_datetime(entry["start_date"],format = '%d/%m/%Y') < min_start_date:
                            min_start_date = pd.to_datetime(entry["start_date"],format = '%d/%m/%Y') 

                        if pd.to_datetime(entry["end_date"],format = '%d/%m/%Y')  > max_end_date:
                            max_end_date = pd.to_datetime(entry["end_date"],format = '%d/%m/%Y')                     
                        
                    row += 1

                wb_start_date = (min_start_date - pd.Timedelta(days=min_start_date.weekday())).date()
                wb_end_date = (max_end_date - pd.Timedelta(days=max_end_date.weekday())).date()
    
                current_date = wb_start_date
    
                columns = ["Opportunity","Capability","Team Member"]
    
                while current_date != wb_end_date:
                    current_date = current_date + pd.Timedelta(days=7)
                    columns.append(str(pd.to_datetime(current_date,format = '%d/%m/%Y').date()))
                    
                df = pd.DataFrame(columns=columns)
                    
                for entry_id,entry in entries.items():
                    nextRow = len(df)
                    working_hours = [entry["monday"],entry["tuesday"],entry["wednesday"],entry["thursday"],entry["friday"]]
                    
                    df.loc[nextRow] = [None] * len(df.columns)
                    df.iloc[nextRow,0] = entry["project"]
                    df.iloc[nextRow,1] = entry["capability"]
                    df.iloc[nextRow,2] = entry["employee"]

                    project_start_date = pd.to_datetime(entry["start_date"],format = '%d/%m/%Y').date()
                    project_end_date = pd.to_datetime(entry["end_date"],format = '%d/%m/%Y').date()
    
                    numCols = len(df.columns)
                    withinRange = False
                    
                    for j in range(3,numCols):
                        week_beginning = pd.to_datetime(df.columns[j]).date()
                        week_beginning = week_beginning - pd.Timedelta(days=week_beginning.weekday())
                        week_end = week_beginning + pd.Timedelta(days=4)
                        hourSum = 0
                        
                        for k in range(0,5):
                            current_date = week_beginning + pd.Timedelta(days=k)
                            if project_start_date <= current_date <= project_end_date:
                                hourSum += int(working_hours[k])

                        df.iloc[nextRow,j] = hourSum
            

                # Convert DataFrame to HTML table with frozen columns
                html_table = dataframe_to_frozen_html_table(df)
            
                # Render HTML in Streamlit
                st.write("Weekly Schedule")
                st.markdown(html_table, unsafe_allow_html=True)
