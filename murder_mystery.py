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
if 'player_character_list' not in st.session_state:
    st.session_state["player_character_list"] = ['Alfred Penrose','Captain Theodore Drake','Charlotte Fontain','Detective Hugh Barrington', \
                                                'Dr. Horace Bellamy','Eleanor Winslow','Isabella Moretti','Lady Vivian Blackthorn', \
                                                'Percy Hargrove','Reginald Reggie Crowley']

image_dict = {
    "Alfred Penrose": "https://raw.githubusercontent.com/rowanb86/PythonApp/main/images/Alfred Penrose.png",
    "Captain Theodore Drake": "https://raw.githubusercontent.com/rowanb86/PythonApp/main/images/Captain Theodore Drake.png",
    "Charlotte Fontain": "https://raw.githubusercontent.com/rowanb86/PythonApp/main/images/Charlotte Fontain.png",
    "Detective Hugh Barrington": "https://raw.githubusercontent.com/rowanb86/PythonApp/main/images/Detective Hugh Barrington.png",
    "Dr. Horace Bellamy": "https://raw.githubusercontent.com/rowanb86/PythonApp/main/images/Dr. Horace Bellamy.png",
    "Eleanor Winslow": "https://raw.githubusercontent.com/rowanb86/PythonApp/main/images/Eleanor Winslow.png",
    "Isabella Moretti": "https://raw.githubusercontent.com/rowanb86/PythonApp/main/images/Isabella Moretti.png",
    "Lady Vivian Blackthorn": "https://raw.githubusercontent.com/rowanb86/PythonApp/main/images/Lady Vivian Blackthorn.png",
    "Percy Hargrove": "https://raw.githubusercontent.com/rowanb86/PythonApp/main/images/Percy Hargrove.png",
    "Reginald Reggie Crowley": "https://raw.githubusercontent.com/rowanb86/PythonApp/main/images/Reginald Reggie Crowley.png"
}

character_desc_dict = {
    "Alfred Penrose": """
    **Role:** Loyal Butler  
    **Description:** A stoic and meticulous servant who has served the family for decades. He knows every secret hidden within the estate.
    """,
    "Captain Theodore Drake": """
    **Role:** Retired Military Officer  
    **Description:** A gruff, disciplined veteran with a sharp tongue and a deep sense of honor. He’s had a mysterious falling-out with the victim years ago.
    """,
    "Charlotte Fontain": """
    **Role:** Ambitious Journalist  
    **Description:** A sharp and ambitious writer always looking for the next big scoop. She was investigating the victim for a scandalous exposé.
    """,
    "Detective Hugh Barrington": """
    **Role:** Police Detective  
    **Description:** A seasoned investigator with a sharp eye for detail and a no-nonsense attitude. He's been called in to solve the case 
    and is determined to expose the truth.    
    """,
    "Dr. Horace Bellamy": """
    **Role:** Eccentric Scholar  
    **Description:** A reclusive historian obsessed with uncovering ancient secrets. He has a strained relationship with the victim, who discredited his research.    
    """,
    "Eleanor Winslow": """
    **Role:** Aspiring Actress  
    **Description:** A bright and beautiful starlet desperate to climb the social ladder. She has ties to nearly everyone at the gathering and hides a few skeletons 
    in her closet.    
    """,
    "Isabella Moretti": """
    **Role:** Mysterious Thief  
    **Description:** A charming and elusive cat burglar known for her daring heists. She was at the scene "by coincidence" but claims she had no interest in the victim.
    """,
    "Lady Vivian Blackthorn": """
    **Role:** Wealthy Socialite  
    **Description:** A glamorous and influential figure who inherited her family’s fortune. She's known for her charm but has a dark history of 
    family feuds.    
    """,
    "Percy Hargrove": """
    **Role:** Brooding Musician  
    **Description:** A talented but troubled violinist who was commissioned to perform at the event. He’s known for his temper and financial struggles.    
    """,
    "Reginald Reggie Crowley": """
    **Role:** Shady Businessman  
    **Description:** A slick, cigar-smoking entrepreneur with a reputation for bending the law. He’s rumored to have been involved in underhanded 
    dealings with the victim.
    """
}

if 'loggedIn' not in st.session_state:
    st.session_state['loggedIn'] = False 

if 'player_in_game' not in st.session_state:
    st.session_state['player_in_game'] = False 

if 'player_character_chosen' not in st.session_state:
    st.session_state['player_character_chosen'] = False 

if "confirm_leave_action" not in st.session_state:
    st.session_state.confirm_action = False



if not firebase_admin._apps:
    # Initialize Firebase
    initialize_app(cred, {
        'databaseURL': 'https://murder-mystery-eb53d-default-rtdb.europe-west1.firebasedatabase.app'
    })

def UpdatePlayerCharacterList(game):
    player_character_list = ['Alfred Penrose','Captain Theodore Drake','Charlotte Fontain','Detective Hugh Barrington', \
                          'Dr. Horace Bellamy','Eleanor Winslow','Isabella Moretti','Lady Vivian Blackthorn', \
                          'Percy Hargrove','Reginald Reggie Crowley']   
    
    ref = db.reference('player_characters')
    players = ref.order_by_child("game").equal_to(game).get() 
    
    if players:
        for player_id,player_data in players.items():
            player_character_list.pop(player_character_list.index(player_data["character"]))

    return(player_character_list)

if 'character_index' not in st.session_state:
    st.session_state["character_index"] = 0

if not st.session_state['loggedIn']:

    st.session_state['username'] = st.text_input("Enter your username:")
    st.session_state['password']  = st.text_input("Enter game password:",key='game_password1',type='password')
    
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
        st.write('You are playing in: ' + st.session_state['game_name'])
    st.session_state['player_character_chosen'] = False

    ref = db.reference("players_in_game")
    players = ref.get()
  
    if players is not None:
      
      for player_id,player_data in players.items():
        if player_data["player"] == st.session_state['username']:
          st.session_state['player_in_game'] = True
          st.session_state['game_name'] = player_data["game"]
          ref = db.reference("player_characters")
          player_characters = ref.order_by_child("game").equal_to(st.session_state['game_name']).get() 

          for player_id,character_data in player_characters.items():
            if character_data["username"] == st.session_state['username']:
              st.session_state["user_character"] = character_data["character"]
              st.session_state['player_character_chosen'] = True
              st.session_state['player_id'] = player_id
              
    if st.session_state['player_in_game']:
        with st.expander("Your character"):
            if st.session_state['player_character_chosen']:
                st.markdown("# " + st.session_state["user_character"])
                st.image(image_dict[st.session_state["user_character"]])
                st.markdown(character_desc_dict[st.session_state["user_character"]]) 

                de_select = st.button("Deselect character")

                if de_select:
                  ref = db.reference(f"player_characters/{st.session_state['player_id']}")
                  ref.delete()
                  st.session_state['player_character_chosen'] = False
                  st.session_state["player_character_list"] = UpdatePlayerCharacterList(st.session_state['game_name'])
                  st.rerun()
          
            else:
                ref = db.reference("player_characters")
                player_characters = ref.get()
              
                if player_characters is not None:
                    st.session_state["player_character_list"] =  UpdatePlayerCharacterList(st.session_state['game_name'])
                    st.session_state["character_index"] = min(st.session_state["character_index"] ,len(st.session_state["player_character_list"])-1)

                player_character_list = st.session_state["player_character_list"]
                st.markdown("# " + player_character_list[st.session_state["character_index"]])
                st.image(image_dict[player_character_list[st.session_state["character_index"]]])
                st.markdown(character_desc_dict[player_character_list[st.session_state["character_index"]]])

                select_character = st.button("Select character")

                if select_character:
                  st.session_state["character_index"] = min(st.session_state["character_index"] ,len(player_character_list)-1)
                  st.session_state["user_character"] = player_character_list[st.session_state["character_index"]]
                  st.session_state['player_character_chosen'] = True 
                  new_player = {"game": st.session_state['game_name'],  "character": st.session_state["user_character"],"username": st.session_state['username']}
                  player_character_list.pop(st.session_state["character_index"])
                  ref.push(new_player)
                  st.rerun()
                
                col1,col2,col3 = st.columns([1, 6, 1]) 

                with col1:
                    st.session_state['back_button'] = st.button('Back')
                
                with col3:
                    st.session_state['next_button'] = st.button('Next')
                    
                if st.session_state['back_button']:
                    st.session_state['character_index'] -= 1
                    st.session_state['character_index'] = max(st.session_state['character_index'],0)
                    st.rerun()
                
                if st.session_state['next_button']:
                    st.session_state['character_index'] += 1
                    st.session_state['character_index'] = min(st.session_state['character_index'],len(player_character_list)-1)
                    st.rerun()
              
        st.markdown('# Players in the game')
        ref = db.reference("player_characters")
        
        player_character_data = ref.order_by_child("game").equal_to(st.session_state['game_name']).get() 
      
        if player_character_data:
          for player_id,player_data in player_character_data.items():
            with st.expander(player_data["character"] + ' (' + player_data["username"] + ')'):
              st.markdown("# " + player_data["character"])
              st.image(image_dict[player_data["character"]])
              st.markdown(character_desc_dict[player_data["character"]]) 

        refresh_player_list = st.button('Refresh player list')
        if refresh_player_list:
          st.rerun()
                
    else:
        with st.expander("Create new game"):
            
            game_name = st.text_input("Enter name of game:")
            password = st.text_input("Enter game password:",key='game_password2',type='password')
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
                        st.session_state['player_in_game'] = True
                        st.session_state['game_name'] = game_name
                        st.write("New game created.")
                        st.rerun()
    
        with st.expander("Join game"):
            ref = db.reference("games")
            games = ref.get()
            games_list = []
    
            if games is not None:
                for game_id, game_data in games.items():
                    games_list.append(game_data["name"])
    
            game_choice = st.selectbox("Choose a game to join:", games_list)
            game_password = st.text_input("Enter game password:",key='game_password3',type='password')
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
                        st.session_state['player_in_game'] = True
                        st.session_state['game_name'] = game_choice
                        st.write('You have joined ' + game_choice + '.')
                        st.rerun()
                else:
                    st.write("Password is incorrect.")

    if st.session_state['player_in_game']: 
        leave_game = st.button("Leave game")

        if leave_game:
            st.session_state.confirm_action = True
    
        if st.session_state.confirm_action:
            st.warning("Are you sure you want to leave the game?")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("Yes, I'm sure"):
                    ref = db.reference("player_characters")
                    player_characters = ref.get() 
                    st.write(st.session_state["username"] )
                    for player_id,player_data in player_characters.items():
                      st.write(player_data["username"] )
                      st.write(st.session_state["username"] )
                      if player_data["username"] == st.session_state["username"]:
                          ref = db.reference(f"player_characters/{player_id}")
                          ref.delete()
                          break
            
                    ref = db.reference("players_in_game")
                    players = ref.get()
                    for player_id,player_data in players.items():
                        if player_data["player"] == st.session_state["username"]:
                          ref = db.reference(f"players_in_game/{player_id}")
                          ref.delete()
                          break                
                    
                    st.session_state['player_character_chosen'] = False
                    st.session_state['player_in_game'] = False
                    st.session_state["player_character_list"] = UpdatePlayerCharacterList(st.session_state["game_name"])
                    #st.session_state.confirm_action = False
                    st.rerun()

            with col2:
                if st.button("No, cancel"):
                    st.info("Action canceled.")
                    #st.session_state.confirm_action = False
    
    log_out = st.button("Log out")  

    if log_out:
        st.session_state["loggedIn"] = False
        st.rerun()
        
        
    
