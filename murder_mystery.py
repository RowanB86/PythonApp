# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 11:33:34 2024

@author: RowanBarua
"""

import streamlit as st
import pandas as pd
import numpy as np
import firebase_admin
from firebase_admin import credentials, initialize_app
import json


username = st.text_input("Enter your username:")
gamename = st.text_input("Enter name of game:")
password = st.text_input("Enter game password:")

new_game = st.button('Create New Game')
join_game = st.button('Join Game')

if new_game:

    if username != '' and gamename != '' and password != '':
        # Load Firebase credentials from Streamlit Secrets
        firebase_credentials = json.loads(st.secrets["firebase"]["service_account_json"])
        cred = credentials.Certificate(firebase_credentials)
        
        # Initialize Firebase
        initialize_app(cred, {
            'databaseURL': 'https://murder-mystery-eb53d-default-rtdb.europe-west1.firebasedatabase.app'
        })

        userExists = True 
        gameExists = True

        ref = db.reference("games") 
        data = ref.get()
        if data is none:
            gameExists = False       

        if userExists = False:
            games = ref.order_by_child("gameName").equal_to(gamename).get() 
            if not games:
                gameExists = False
        
        if gameExists:
            st.write("A game with this name has already been created".)
        else:
            game_data = {"name": gamename, "password": password, "host": username}
            ref.push(game_data)
            st.write("New game created.")
            
        
        
        
