import streamlit as st
import pandas as pd
from streamlit_ace import st_ace
import pandasql as ps

if 'dataframes' not in st.session_state:
    st.session_state.dataframes = {}
 
uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx", "xls"])

if uploaded_file:
    excel_file = pd.ExcelFile(uploaded_file)
    sheet_names = excel_file.sheet_names

    selected_sheet = st.selectbox("Select a sheet", sheet_names)

    dataframe_name = st.text_input("Enter table name")
    
    if st.button("Add table"):

        if selected_sheet and dataframe_name:

            df = excel_file.parse(selected_sheet)

            st.session_state.dataframes[dataframe_name] = df 

            st.write("Table added")

selected_table = st.selectbox("Select a table to view", options=list(st.session_state.dataframes.keys()))

if selected_table:

    st.dataframe(st.session_state.dataframes[selected_table])

query = st_ace(language="sql", placeholder="Write your SQL query here...")

if st.button("Execute SQL query"):
    try:
        # Execute the SQL query using pandasql
        result = ps.sqldf(query, st.session_state.dataframes)
        st.write("Query Result:")
        st.dataframe(result)
    except Exception as e:
        st.error(f"Error executing query: {e}")
