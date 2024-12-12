# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 11:33:34 2024

@author: RowanBarua
"""

import streamlit as st
import pandas as pd
import numpy as np
import firebase_admin
from firebase_admin import credentials, initialize_app, db
import json

st.write(f"Streamlit version: {st.__version__}")
# Load Firebase credentials from Streamlit Secrets
firebase_credentials = json.loads(st.secrets["firebase"]["service_account_json"])
cred = credentials.Certificate(firebase_credentials)

if 'loggedIn' not in st.session_state:
    st.session_state['loggedIn'] = False 

if not firebase_admin._apps:
    # Initialize Firebase
    initialize_app(cred, {
        'databaseURL': 'https://murder-mystery-eb53d-default-rtdb.europe-west1.firebasedatabase.app'
    })

username = st.text_input("Enter your username:")
password = st.text_input("Enter game password:")

create_account = st.button("Create Account")
log_in = st.button("Log in")

usernameExists = True 

ref = db.reference("accounts") 
data = ref.get()
if data is None:
    usernameExists = False

usernames = ref.order_by_child("username").equal_to(username).get() 

if usernames is None:
    usernameExists = False

if create_account:
    if usernameExists:
        st.write("An account with this username already exists.")
    else:
        new_user = {"username": username, "password": password, "host": username}
        ref.push(new_user)
        st.write("Account created.")

if log_in:
    if usernameExists:
        usernames = ref.order_by_child("username").equal_to(username).get() 
        user_id, user_data = next(iter(usernames.items()))

        if user_data["password"] == password:
            st.session_state['loggedIn'] = True
            
        else:

            st.write("Password is incorrect.")
        
    else:
        st.write("Username not recognised.")
                 
if st.session_state['loggedIn']:

    st.write("You are logged in  as: " + username)
    
    new_game = st.button('Create New Game')
    join_game = st.button('Join Game')
    gamename = st.text_input("Enter name of game:")
    
    if new_game:
    
        if username != '' and gamename != '' and password != '':

            userExists = True 
            gameExists = True
    
            ref = db.reference("games") 
            data = ref.get()
            if data is None:
                gameExists = False       
    
            if gameExists == True:
                games = ref.order_by_child("name").equal_to(gamename).get() 
                if not games:
                    gameExists = False
            
            if gameExists:
                st.write("A game with this name has already been created.")
            else:
                game_data = {"name": gamename, "password": password, "host": username}
                ref.push(game_data)
                st.write("New game created.")

    log_out = st.button("Log out")

    if log_out:
        st.session_state["loggedIn"] = False
        
        
    
