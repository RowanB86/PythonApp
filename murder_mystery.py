# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 11:33:34 2024

@author: RowanBarua
"""

import streamlit as st
import pyodbc
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pymssql
import traceback
import textwrap
from streamlit_ace import st_ace
import firebase_admin
from firebase_admin import credentials, initialize_app
import json


username = st.text_input("Enter your name:")
gamename = st.text_input("Enter name of game:")
password = st.text_input("Enter game password:")

new_game = st.button('Create New Game')
join_game = st.button('Join Game')

if new_game:

    # Load Firebase credentials from Streamlit Secrets
    firebase_credentials = json.loads(st.secrets["firebase"]["service_account_json"])
    cred = credentials.Certificate(firebase_credentials)
    
    # Initialize Firebase
    initialize_app(cred, {
        'databaseURL': 'https://murder-mystery-eb53d-default-rtdb.europe-west1.firebasedatabase.app'
    })
