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

# Load Firebase credentials from Streamlit Secrets
firebase_credentials = json.loads(st.secrets["firebase"]["service_account_json"])
cred = credentials.Certificate(firebase_credentials)

image_dict = {
    "Image 1": "https://raw.githubusercontent.com/rowanb86/PythonApp/main/images/Alfred Penrose.png",
    "Image 2": "https://raw.githubusercontent.com/rowanb86/PythonApp/main/images/Captain Theodore Drake.png",
    "Image 3": "https://raw.githubusercontent.com/rowanb86/PythonApp/main/images/Charlotte Fontain.png",
    "Image 4": "https://raw.githubusercontent.com/rowanb86/PythonApp/main/images/Detective Hugh Barrington.png",
    "Image 5": "https://raw.githubusercontent.com/rowanb86/PythonApp/main/images/Dr. Horace Bellamy.png",
    "Image 6": "https://raw.githubusercontent.com/rowanb86/PythonApp/main/images/Eleanor Winslow.png",
    "Image 7": "https://raw.githubusercontent.com/rowanb86/PythonApp/main/images/Isabella Moretti.png",
    "Image 8": "https://raw.githubusercontent.com/rowanb86/PythonApp/main/images/Lady Vivian Blackthorn.png",
    "Image 9": "https://raw.githubusercontent.com/rowanb86/PythonApp/main/images/Percy Hargrove.png",
    "Image 10": "https://raw.githubusercontent.com/rowanb86/PythonApp/main/images/Reginald Reggie Crowley.png"
}

if 'loggedIn' not in st.session_state:
    st.session_state['loggedIn'] = False 

if 'player_in_game' not in st.session_state:
    st.session_state['player_in_game'] = False 

if not firebase_admin._apps:
    # Initialize Firebase
    initialize_app(cred, {
        'databaseURL': 'https://murder-mystery-eb53d-default-rtdb.europe-west1.firebasedatabase.app'
    })

if not st.session_state['loggedIn']:

    st.session_state['username'] = st.text_input("Enter your username:")
    st.session_state['password']  = st.text_input("Enter game password:",key='game_password1')
    
    create_account = st.button("Create Account")
    st.session_state['log_in'] = st.button("Log in")
    
    usernameExists = True 
    
    ref = db.reference("accounts") 
    data = ref.get()
    if data is None:
        usernameExists = False
    
    usernames = ref.order_by_child("username").equal_to(st.session_state['username']).get() 
    
    if not usernames:
        usernameExists = False
    
    if create_account:
        if usernameExists:
            st.write("An account with this username already exists.")
        else:
            new_user = {"username": st.session_state['username'], "password": st.session_state['password']}
            ref.push(new_user)
            st.write("Account created.")

    if st.session_state['log_in']:
        if usernameExists:
            usernames = ref.order_by_child("username").equal_to(st.session_state['username']).get() 
            user_id, user_data = next(iter(usernames.items()))
    
            if user_data["password"] == st.session_state['password']:
                st.session_state['loggedIn'] = True
                st.rerun()                
            else:
                st.write("Password is incorrect.")
        else:
            st.write("Username not recognised.")
                 
if st.session_state['loggedIn']:

    st.write("You are logged in  as: " + st.session_state['username'])

    if st.session_state['player_in_game']:

    else:
        with st.expander("Create new game"):
            
            game_name = st.text_input("Enter name of game:")
            password = st.text_input("Enter game password:",key='game_password2')
            new_game = st.button('Create New Game')
            
            if new_game:
            
                if st.session_state['username'] != '' and game_name != '' and password != '':
        
                    userExists = True 
                    gameExists = True
            
                    ref = db.reference("games") 
                    data = ref.get()
                    if data is None:
                        gameExists = False       
            
                    if gameExists == True:
                        games = ref.order_by_child("name").equal_to(game_name).get() 
                        if not games:
                            gameExists = False
                    
                    if gameExists:
                        st.write("A game with this name has already been created.")
                    else:
                        game_data = {"name": game_name, "password": password, "host": st.session_state['username']}
                        ref.push(game_data)
                        ref = db.reference("players_in_game") 
                        player_game_data = {"game": game_name, "player": st.session_state['username']}
                        ref.push(player_game_data)
                        
                        st.write("New game created.")
    
        with st.expander("Join game"):
            ref = db.reference("games")
            games = ref.get()
            games_list = []
    
            if games is not None:
                for game_id, game_data in games.items():
                    games_list.append(game_data["name"])
    
            game_choice = st.selectbox("Choose a game to join:", games_list)
            game_password = st.text_input("Enter game password:",key='game_password3')
            join_game = st.button('Join Game')
            refresh_game_list = st.button('Refresh game list')
    
            if join_game and game_choice is not None:
                games = ref.order_by_child("name").equal_to(game_choice).get() 
                game_id, game_data = next(iter(games.items()))
    
                if game_data["password"] == game_password:
                    playerInGame = False
                    ref = db.reference("players_in_game")
                    players_in_game = ref.order_by_child("game").equal_to(game_choice).get() 
    
                    for player_game_id, game_player_data in players_in_game.items():
                        if game_player_data["player"] == st.session_state['username']:
                            playerInGame = True
    
                    if playerInGame:
                        st.write("You are already in this game.")
                    else:
                        player_game_data = {"game": game_choice, "player": st.session_state['username']}
                        ref.push(player_game_data)
                        st.write('You have joined ' + game_choice + '.')
                else:
                    st.write("Password is incorrect.")
                    

    log_out = st.button("Log out")

    if log_out:
        st.session_state["loggedIn"] = False
        st.rerun()
        
        
    
