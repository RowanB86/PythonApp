

import streamlit as st
import pandas as pd
import numpy as np
import firebase_admin
from firebase_admin import credentials, initialize_app, db
import json
import openai
import re
import sqlite3
import textwrap

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

def save_dataframe_to_firebase(df, df_name):

    disallowed_chars = [r"\\",r"\.",r"/",r"#",r"\$",r"\[",r"\]",r"\*"," "]
    valid = True

    for i in range(0,len(disallowed_chars)):
        if re.search(disallowed_chars[i],df_name):
            valid = False

    if not valid:
        return "Dataframe name must not include any of the following characters; \"\,/,.,#,$,[,],*\" or spaces."
    else:

        
        ref = db.reference(df_name)
        if ref.get() is not None:
            return f"A dataframe named; {df_name} already exists."
        else:
            df.replace(np.nan, None, inplace=True)
            ref.set(df.to_dict(orient="records"))
            ref = db.reference("Datasets")
            new_dataset = {"dataset": df_name}
            ref.push(new_dataset)
    
            return "Dataframe saved."
    
def load_dataframe(df_name):
    if df_name is not None:
        ref = db.reference(df_name)
        df = ref.get()
    
        if df is not None:
            return pd.DataFrame(df)
        else:
            return pd.DataFrame()
    else:
        return pd.DataFrame()

def SQLTransform(SQL_code):
    code = textwrap.dedent("""
    import pandas as pd
    import sqlite3
    conn = sqlite3.connect(":memory:")

    """)
    ref = db.reference("Datasets")
    datasets = ref.get()
    
    for dataset_id,dataset in datasets.items():
        code += f"ref = db.reference(\"{dataset["dataset"]}\")\n"
        code += "df = ref.get()\n"
        code += textwrap.dedent(f"{dataset["dataset"]} = pd.DataFrame(df)\n")
        
    for dataset_id,dataset in datasets.items():
        code += f"{dataset["dataset"]}.to_sql(\"users\", conn, index=False, if_exists\"replace\")\n"

    
    code = code + f"SQL_code = '{SQL_code}'" + "\n"
    
    
    code = code + textwrap.dedent("""
    df = pd.read_sql_query(SQL_code, conn)
    conn.close()
    """)

    
    
    return code

    
