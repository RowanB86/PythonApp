import streamlit as st
import pandas as pd
from streamlit_ace import st_ace
import pandasql as ps

if 'dataframes' not in st.session_state:
    st.session_state.dataframes = {}
 
