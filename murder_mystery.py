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
import openai

openai.api_key = st.secrets["openai"]["api_key"]

# Load Firebase credentials from Streamlit Secrets
firebase_credentials = json.loads(st.secrets["firebase"]["service_account_json"])
cred = credentials.Certificate(firebase_credentials)
if 'player_character_list' not in st.session_state:
    st.session_state["player_character_list"] = ['Alfred Penrose','Captain Theodore Drake','Charlotte Fontain','Detective Hugh Barrington', \
                                            'Dr. Horace Bellamy','Eleanor Winslow','Isabella Moretti','Lady Vivian Blackthorn', \
                                            'Percy Hargrove','Reginald Reggie Crowley']

if 'game_has_started' not in st.session_state:
    st.session_state["game_has_started"] = False

game_rules = """
Each character is allowed to explore locations and will each have 3 personal objectives \
                        to complete by the end of the game. There is no limit to the number of rounds that can be played. \
                        Characters will be able to do things like use items from their inventory to perform actions, talk to other characters they encounter \
                        in the game (both playing and non-playing). At least one of the 10 characters should be involved in committing the murder. A detective 
                        is allowed to pose five questions to any player they like once per round, regardless of whether they're in the same room as the player.
                        A player questioned by a detective is able to respond to these questions regardless of if they're in the same room. Other characters are
                        only able to communicate with one another if they're in the same room and characters should not ask another character more than two questions
                        per round. Any character is allowed to pose up to 2 questions to any other character in the same room as them.
"""
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

locations = {
"Grand Ballroom": {
    "description": "A lavish room with glittering chandeliers and ornate decorations. The site of the last known gathering before the murder."
},
"Library": {
    "description": "A quiet, dusty space filled with rows of ancient books and hidden alcoves. It holds the secrets of many family scandals."
},
"Wine Cellar": {
    "description": "A dimly lit, musty cellar stocked with vintage wines and dark corners. An ideal place for hiding secrets—or bodies."
},
"Garden Maze": {
    "description": "A sprawling hedge maze with narrow pathways and a central fountain. It's easy to get lost here, especially in the dark."
},
"Master Bedroom": {
    "description": "An opulent room with heavy drapes and a locked chest at the foot of the bed. Rumors say it holds incriminating documents."
},
"Kitchen": {
    "description": "A bustling space with gleaming knives and bubbling pots. The staff often gossip here about the guests' movements."
},
"Study": {
    "description": "A small room with a large oak desk and scattered papers. The scene of many heated arguments and secret deals."
}
}

if 'loggedIn' not in st.session_state:
    st.session_state['loggedIn'] = False 

if 'player_in_game' not in st.session_state:
    st.session_state['player_in_game'] = False 

if 'player_character_chosen' not in st.session_state:
    st.session_state['player_character_chosen'] = False 

if "confirm_leave_action" not in st.session_state:
    st.session_state.confirm_action = False

if 'leave_game_button' not in st.session_state:
    st.session_state['leave_game_button']  = False

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

def leave_game(game_name,username):
    st.session_state.confirm_action = True

    ref = db.reference("player_characters")
    player_characters = ref.get() 
    for player_id,player_data in player_characters.items():
        if player_data["username"] == username:
            ref = db.reference(f"player_characters/{player_id}")
            ref.delete()
            break
    
    ref = db.reference("players_in_game")
    players = ref.get()
    for player_id,player_data in players.items():
        if player_data["player"] == username:
            ref = db.reference(f"players_in_game/{player_id}")
            ref.delete()
            break                
    
    st.session_state['player_character_chosen'] = False
    st.session_state['player_in_game'] = False
    st.session_state["player_character_list"] = UpdatePlayerCharacterList(game_name)

def generate_action(game,character):
    ref = db.reference("backstories")
    games = ref.order_by_child("game_name").equal_to(game).get() 

    for game_id,game_data in games.items():
        backstory = game_data["backstory"]

    ref = db.reference("items")
    items = ref.order_by_child("game").equal_to(game).get() 

    ref = db.reference("objectives")
    objectives = ref.order_by_child("game").equal_to(game).get() 

    ref = db.reference("character_viewpoints")
    viewpoints = ref.order_by_child("game").equal_to(game).get() 
    
    ref = db.reference("events")
    if ref:
        events = ref.order_by_child("game").equal_to(game).get() 
    
    messages = [{"role": "system", "content": "You are the game master for a murder mystery game."}]
    messages += [{"role": "assistant", "content": f"Character: {char}"} for char in character_desc_dict.values()]
    messages += [{"role": "assistant", "content": f"Location: {location}"} for location in locations.values()]
    messages += [{"role": "assistant", "content": f"Game Rules: {game_rules}"}]
    messages += [{"role": "assistant", "content": f"Back story to the game (only you know this story. The players of the game don't.): {backstory}"}]

    if items is not None:
        for item_id,item_data in items.items():
            messages += [{"role": "assistant", "content": f"This is an item belonging to {item_data["character"]}: {item_data["item"]}"}]

    if objectives is not None:
        for objective_id,objectives_data in objectives.items():
            messages += [{"role": "assistant", "content": f"This is one of {objectives_data["character"]}'s objectives: {objectives_data["objective"]}"}]

    if viewpoints is not None:
        for viewpoint_id,viewpoints_data in viewpoints.items():
            messages += [{"role": "assistant", "content": f"This is the perspective of {viewpoints_data["character"]}: {viewpoints_data["viewpoint"]}"}]

    if events is not None:
        for event_id, events_data in events.items():
            messages += [{"role": "assistant", "content": f"This was an event involving {events_data["character"]} and performed in round {events_data["round"]}: {events_data["event"]}"}]

    messages += [{"role": "user", "content": f"{character} is a character that I want you to control. Please carefully assess the events that have occurred in the game so \
    so far, the backstory, {character}'s items and objectives and describe an action that {character} could attempt to perform in order to help fulfil their objectives. \
    Pay close attention to events that have occurred that may have directly affected {character}, that they have not yet responded to e.g. if another player character has \
    posed a question to {character} and {character} has not yet responded, it would make sense that {character} chooses to  respond to that question in some way even if \
    they choose not to give much of an answer to the question (they may give an evasive answer). Other actions might involve exploring a location or using one of their \
    items to interact with their environment. Please only describe the action that they attempt. Do not include any consequence of their action."}]

    response = openai.ChatCompletion.create(model="gpt-4o-mini",messages=messages)
    action_submitted = response["choices"][0]["message"]["content"] 

    return action_submitted

def submit_action(game,character,action):
        ref = db.reference("backstories")
        games = ref.order_by_child("game_name").equal_to(game).get() 

        for game_id,game_data in games.items():
            backstory = game_data["backstory"]

        ref = db.reference("items")
        items = ref.order_by_child("game").equal_to(game).get() 

        ref = db.reference("objectives")
        objectives = ref.order_by_child("game").equal_to(game).get() 

        ref = db.reference("character_viewpoints")
        viewpoints = ref.order_by_child("game").equal_to(game).get() 
        
        ref = db.reference("events")
        if ref:
            events = ref.order_by_child("game").equal_to(game).get() 
        
        messages = [{"role": "system", "content": "You are the game master for a murder mystery game."}]
        messages += [{"role": "assistant", "content": f"Character: {char}"} for char in character_desc_dict.values()]
        messages += [{"role": "assistant", "content": f"Location: {location}"} for location in locations.values()]
        messages += [{"role": "assistant", "content": f"Game Rules: {game_rules}"}]
        messages += [{"role": "assistant", "content": f"Back story to the game (only you know this story. The players of the game don't.): {backstory}"}]

        if items is not None:
            for item_id,item_data in items.items():
                messages += [{"role": "assistant", "content": f"This is an item belonging to {item_data["character"]}: {item_data["item"]}"}]

        if objectives is not None:
            for objective_id,objectives_data in objectives.items():
                messages += [{"role": "assistant", "content": f"This is one of {objectives_data["character"]}'s objectives: {objectives_data["objective"]}"}]

        if viewpoints is not None:
            for viewpoint_id,viewpoints_data in viewpoints.items():
                messages += [{"role": "assistant", "content": f"This is the perspective of {viewpoints_data["character"]}: {viewpoints_data["viewpoint"]}"}]

        if events is not None:
            for event_id, events_data in events.items():
                messages += [{"role": "assistant", "content": f"This was an event involving {events_data["character"]} and performed in round {events_data["round"]}: {events_data["event"]}"}]

        
        messages += [{"role": "assistant", "content": f"{character} has made a request to perform the following action: {action}."}]
        messages += [{"role": "user", "content": f"Please carefully assess the action that {character} has requested to make, the backstory, the rules of the game, the events \
        that have occurred in the game up till this point and all other relevant information, decide whether the requested action is permissible within the rules of the game and determine a realistic outcome of the action. Be careful to  \
        check that the requested action will not take the character beyond the limits of what they are permitted. If a question is posed to one of the other 9 player characters, record the details of the question that was asked, but do not respond on the player character's behalf. The player \
        character is controlled by a human who will have the chance to respond to the question themselves. Please return a description of the action performed and the outcome in a way that will be \
        informative to the character who attempted the action and also suitable to be recorded in an events log that will be fed back to you as the game progresses."}]

        response = openai.ChatCompletion.create(model="gpt-4o-mini",messages=messages)
        event = response["choices"][0]["message"]["content"] 

        messages = [{"role": "system", "content": "You are the game master for a murder mystery game."}]
        messages += [{"role": "assistant", "content": f"This is a record of an event that occurred in the game as the result of an action that was performed by a player character: {event}."}]
        messages += [{"role": "user", "content": "Extract (return) the part of the description of the event that will inform the user of the result of their action and nothing more. If a \
        question was posed by one player character to another, make sure you include the question that was asked, but do not include the response of the player character that was asked the \
        question as they are controlled by a human who will have the opportunity to respond themselves. The player characters are; 'Alfred Penrose','Captain Theodore Drake','Charlotte Fontain',\
        'Detective Hugh Barrington','Dr. Horace Bellamy','Eleanor Winslow', 'Isabella Moretti','Lady Vivian Blackthorn','Percy Hargrove','Reginald Reggie Crowley'.If a non-player character is \
        asked a question, you can include their response."}]

        response = openai.ChatCompletion.create(model="gpt-4o-mini",messages=messages)
        event2 = response["choices"][0]["message"]["content"]
        
        
        messages = [{"role": "system", "content": "You are the game master for a murder mystery game."}]
        messages += [{"role": "assistant", "content": f"This is a record of an event that occurred in the game as the result of an action that was performed by a player character: {event}."}]
        messages += [{"role": "user", "content": "Extract (return) the part of the description of the event that will be suitable to be recorded in an events log that \
        will later be fed back to you as the game progresses. There are 10 player characters in the game. If a question was posed by one player character to another, make sure you include \
        the question that was asked, but do not include the response of the player character that was asked the question as they are controlled by a human who will have the opportunity to \
        respond themselves. The player characters are; 'Alfred Penrose','Captain Theodore Drake','Charlotte Fontain','Detective Hugh Barrington','Dr. Horace Bellamy','Eleanor Winslow', \
        'Isabella Moretti','Lady Vivian Blackthorn','Percy Hargrove','Reginald Reggie Crowley'. If a non-player character is asked a question, you can include their response. \
        Try to do this with as few tokens as possible whilst retaining the important nuances of the event."}]

        response = openai.ChatCompletion.create(model="gpt-4o-mini",messages=messages)
        event = response["choices"][0]["message"]["content"]

        return event,event2

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
    if st.session_state["game_has_started"]:
        ref = db.reference("game_progression")
        games = ref.order_by_child("game").equal_to(st.session_state['game_name']).get() 
        for game_ID,game in games.items():
            st.write("The game is in Round: " + str(game["round"]))
            st.session_state["round_number"] = game["round"]
    
    refresh_game = st.button("Refresh Game")

    if refresh_game:
        st.rerun()
    
    st.session_state["user_is_host"] = False
    
    ref = db.reference("games")
    games = ref.get()

    if games is not None:
        for game_id,game_data in games.items():
            st.session_state["game_name"] = game_data["name"]
            if game_data["host"] == st.session_state['username']:
                st.session_state["user_is_host"] = True

        ref = db.reference("game_progression")
        games = ref.order_by_child("game").equal_to(st.session_state['game_name']).get() 
    
        st.session_state["game_has_started"] = False
        if games is not None:
            for game_id,game_data in games.items():
                if game_data["round"] > 0:
                    st.session_state["game_has_started"] = True
        
    if 'user_is_host' in st.session_state and st.session_state["game_has_started"] == False:
        if st.session_state["user_is_host"]:
            start_game = st.button("Start_Game",key="start_game_as_host")
                      
            if start_game:
                st.session_state['game_has_started'] = True
                messages = [{"role": "system", "content": "You are the game master for a murder mystery game."}]
                messages += [{"role": "assistant", "content": f"Character: {char}"} for char in character_desc_dict.values()]
                messages += [{"role": "assistant", "content": f"Location: {location}"} for location in locations.values()]
                messages += [{"role": "assistant", "content": f"Game Rules: {game_rules}"}]
                messages += [{"role": "user", "content": "Please create a plot that details intricate dynamics between the characters of a murder mystery game and events that occurred in accordance with \
                              the locations that each character will later explore. Players will not see this story, but you will refer to it throughout the game when processing events \
                              that occur. Please make the plot intricate in order to inspire an interesting game. At least one of the 10 characters should have been involved in committing the murder. \
                              Try to do this with as few tokens as possible because this plot will be fed back to you every time \
                              a new event in the game occurs. Create a plot that you will be able to easily and efficiently process later on. Do not add anything superfluous."}]

                placeholder = st.empty()
                placeholder.write("Generating backstory.")
                response = openai.ChatCompletion.create(
                       model="gpt-4o-mini",
                       messages=messages)

                backstory = response["choices"][0]["message"]["content"]
                ref = db.reference("backstories")
                game_data = {"game_name": st.session_state['game_name'], "backstory":  backstory}
                ref.push(game_data)
                placeholder.write("Backstory created.")

                ref = db.reference("objectives")
                num_characters = len(character_desc_dict)
                objectives = []
                
                for character in character_desc_dict.keys():
                    for j in range(0,3):
                            messages = [{"role": "system", "content": "You are the game master for a murder mystery game."}]
                            messages += [{"role": "assistant", "content": f"Character: {char}"} for char in character_desc_dict.values()]
                            messages += [{"role": "assistant", "content": f"Location: {location}"} for location in locations.values()]
                            messages += [{"role": "assistant", "content": f"Game Rules: {game_rules}"}]
                            messages += [{"role": "assistant", "content": f"Back story to the game: {backstory}"}]
                            
                            for k in range(0,len(objectives)):
                                messages += [{"role": "assistant", "content": f"{objectives[k]}"}]
                                
                            if j == 0:
                                placeholder.write(f"Generating {character}'s first objective")
                                messages += [{"role": "user", "content": f"Please come up with the first of three objectives (there will be three in total) that {character} will aim to  \
                                fulfil throughout the course of the game. Only return the details of the objective. The content you produce will appear on this character's \
                                objectives list. Do not generate anything superfluous."}]
                                prefix = f"{character}'s first objective is: "
                            elif j == 1:
                                placeholder.write(f"Generating {character}'s second objective")
                                messages += [{"role": "user", "content": f"Please come up with a second of three objectives (there will be three in total) that {character} will aim to  \
                                fulfil throughout the course of the game. Only return the details of the objective. The content you produce will appear on this character's \
                                objectives list. Do not generate anything superfluous."}]  
                                prefix = f"{character}'s second objective is: "
                            elif j == 2:
                                placeholder.write(f"Generating {character}'s third objective")
                                messages += [{"role": "user", "content": f"Please come up with a final, third objective that {character} will aim to  \
                                fulfil throughout the course of the game. Only return the details of the objective. The content you produce will appear on this character's \
                                objectives list. Do not generate anything superfluous."}]    
                                prefix = f"{character}'s third objective is: "

                            response = openai.ChatCompletion.create(
                                       model="gpt-4o-mini",
                                       messages=messages)

                            objective = response["choices"][0]["message"]["content"] 
                            objectives.append(prefix + objective)
                            new_objective = {"game": st.session_state['game_name'], "character": character, "objective": objective}
                            ref.push(new_objective)
                        
                placeholder.write("Objectives generated")       

                ref = db.reference("items")
                num_characters = len(character_desc_dict)
                items = []
                
                for character in character_desc_dict.keys():
                    for j in range(0,3):
                            messages = [{"role": "system", "content": "You are the game master for a murder mystery game."}]
                            messages += [{"role": "assistant", "content": f"Character: {char}"} for char in character_desc_dict.values()]
                            messages += [{"role": "assistant", "content": f"Location: {location}"} for location in locations.values()]
                            messages += [{"role": "assistant", "content": f"Game Rules: {game_rules}"}]
                            messages += [{"role": "assistant", "content": f"Back story to the game: {backstory}"}]
                            
                            for k in range(0,len(objectives)):
                                messages += [{"role": "assistant", "content": f"{objectives[k]}"}]

                            for k in range(0,len(items)):
                                messages += [{"role": "assistant", "content": f"{items[k]}"}]
                                
                            if j == 0:
                                placeholder.write(f"Generating {character}'s first item")
                                messages += [{"role": "user", "content": f"Please come up with the first of three items (there will be three in total) that {character} might be able to use   \
                                to help fulfil their objectives. Only return the details of the item. The content you produce will appear on this character's \
                                inventory list. Do not generate anything superfluous."}]
                                prefix = f"{character}'s first item is: "
                            elif j == 1:
                                placeholder.write(f"Generating {character}'s second item")
                                messages += [{"role": "user", "content": f"Please come up with a second of three items (there will be three in total) that {character} might be able to use   \
                                to help fulfil their objectives. Only return the details of the item. The content you produce will appear on this character's \
                                inventory list. Do not generate anything superfluous."}]
                                prefix = f"{character}'s second item is: "
                            elif j == 2:
                                placeholder.write(f"Generating {character}'s third item")
                                messages += [{"role": "user", "content": f"Please come up with a final, third item that {character} might be able to use  \
                                to help fulfil their objectives. Only return the details of the item. The content you produce will appear on this character's \
                                inventory list. Do not generate anything superfluous."}]    
                                prefix = f"{character}'s third item is: "

                            response = openai.ChatCompletion.create(
                                       model="gpt-4o-mini",
                                       messages=messages)

                            item = response["choices"][0]["message"]["content"] 
                            items.append(prefix + item)
                            new_item = {"game": st.session_state['game_name'], "character": character, "item": item}
                            ref.push(new_item)
                placeholder.write("Items generated")

                ref = db.reference("character_viewpoints")
                viewpoints = []

                for character in character_desc_dict.keys():
                    placeholder.write(f"Generating {character}'s 'Character Viewpoint'")
                    messages = [{"role": "system", "content": "You are the game master for a murder mystery game."}]
                    messages += [{"role": "assistant", "content": f"Character: {char}"} for char in character_desc_dict.values()]
                    messages += [{"role": "assistant", "content": f"Location: {location}"} for location in locations.values()]
                    messages += [{"role": "assistant", "content": f"Game Rules: {game_rules}"}]
                    messages += [{"role": "assistant", "content": f"Back story to the game: {backstory}"}]
                    
                    for k in range(0,len(objectives)):
                        messages += [{"role": "assistant", "content": f"{objectives[k]}"}]
    
                    for k in range(0,len(items)):
                        messages += [{"role": "assistant", "content": f"{items[k]}"}]   
    
                    messages += [{"role": "user", "content": f"In accordance with the backstory to the game and all other information you have about the \
                    narrative surrounding the game, please can you detail {character}'s 'Character Viewpoint' i.e. what information the character has about the \
                    events that have occurred in the game or any secrets this character knows that other characters might not. The response that you generate \
                    will be visible to this particular character and appear in their 'Character Viewpoint' section. Be careful not to miss key details in the backstory that are relevant \
                    to the player character e.g. if the character committed the murder, it is important that this appears in their 'Character Viewpoint'. Please do not generate anything \
                    superfluous."}]

                    response = openai.ChatCompletion.create(model="gpt-4o-mini",messages=messages)
                    viewpoint = response["choices"][0]["message"]["content"] 
                    character_viewpoint = {"game": st.session_state['game_name'], "character": character, "viewpoint": viewpoint}
                    ref.push(character_viewpoint)

                placeholder.write("Character viewpoints generated.")

                ref = db.reference("game_progression")
                games = ref.order_by_child("game").equal_to(st.session_state['game_name']).get() 
                for game_id,game in games.items():
                    game_id = game_id

                ref = db.reference(f"game_progression/{game_id}")
                ref.update({"round": 1})
    elif "user_is_host" in st.session_state:
        generate_ai_character_moves = st.button("Generate AI character moves")
        
        if generate_ai_character_moves:
            game_characters =   ['Alfred Penrose','Captain Theodore Drake','Charlotte Fontain','Detective Hugh Barrington', \
                                  'Dr. Horace Bellamy','Eleanor Winslow','Isabella Moretti','Lady Vivian Blackthorn', \
                                  'Percy Hargrove','Reginald Reggie Crowley']
          
            ref = db.reference("player_characters")
            players = ref.order_by_child("game").equal_to(st.session_state['game_name']).get() 
            for player_id,player in players.items():
                if player["character"] in game_characters:
                    game_characters.pop(player["character"])
        
            for i in range(0,len(game_characters)):
                st.write("Generating " + game_characters[i] + "'s actions.")
                action_submitted = generate_action(st.session_state['game_name'],game_characters[i])
                event = submit_action(st.session_state['game_name'],game_characters[i],action_submitted)
                ref = db.reference("events")
                new_event = {"game": st.session_state['game_name'], "character": game_characters[i], "round": st.session_state["round_number"],"event": event}
                ref.push(new_event)
                      
    ref = db.reference("players_in_game")

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
                    
        if st.session_state["game_has_started"]:
            with st.expander("Locations"):
                for location in locations.keys():
                    
                    st.markdown('# ' + location)
                    st.markdown(locations[location]["description"])
    
            with st.expander("Inventory"):
                ref = db.reference("items")
                items = ref.order_by_child("game").equal_to(st.session_state['game_name']).get() 
    
                if items is not None:
                    for item_id,item_data in items.items():
                        if item_data["character"] == st.session_state["user_character"]:
                            st.write(item_data["item"] + '\n')
                        
            with st.expander("Objectives"):
                ref = db.reference("objectives")
                objectives = ref.order_by_child("game").equal_to(st.session_state['game_name']).get() 
    
                if objectives is not None:
                    for objective_id,objective_data in objectives.items():
                        if objective_data["character"] == st.session_state["user_character"]:
                            st.write(objective_data["objective"] + '\n')                
    
            with st.expander("Character Viewpoint"):
                ref = db.reference("character_viewpoints")
                viewpoints = ref.order_by_child("game").equal_to(st.session_state['game_name']).get() 
    
                if viewpoints is not None:
                    for viewpoint_id,viewpoint_data in viewpoints.items():
                        if viewpoint_data["character"] == st.session_state["user_character"]:
                            st.write(viewpoint_data["viewpoint"])

            with st.expander("Perform an action"):
                action = st.text_input("Describe an action that you would like to perform")
                submit_action = st.button("Submit Action")
                placeholder2 = st.empty()
                if submit_action:
                    event = submit_action(st.session_state['game_name'], st.session_state["user_character"],action)
                    
                    ref = db.reference("events")
                    new_event = {"game": st.session_state['game_name'], "character": st.session_state["user_character"], "round": st.session_state["round_number"],"event": event[0]}
                    ref.push(new_event)
                    placeholder2.write(event[1])

        with st.expander("Events log"): 
            get_events_update = st.button("Get events update")
            events_placeholder = st.empty()

            if get_events_update:
                messages = [{"role": "system", "content": "You are the game master for a murder mystery game."}]
                ref = db.reference("events")
                if ref:
                    events = ref.order_by_child("game").equal_to(st.session_state['game_name']).get()
                    if events is not None:
                        for event_id,event in events.items():
                            messages += [{"role": "assistant", "content": f"This was an event involving {event["character"]} and performed in round {event["round"]}: {event["event"]}"}]
    
                messages += [{"role": "user", "content": f"Please assess all events that have occurred in the game and provide the player a log of all events that player character; \
                {st.session_state['user_character']} would realistically have been aware of in the game e.g. a question that was posed to him by another character in the game or an action that the \
                character performed."}]
                response = openai.ChatCompletion.create(model="gpt-4o-mini",messages=messages)
                events_log = response["choices"][0]["message"]["content"]
                events_placeholder.write(events_log)

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
                        ref = db.reference("game_progression")
                        new_game_data = {"game": game_name, "round": 0}
                        ref.push(new_game_data)

                        
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
        leave_game_button = st.button("Leave game")

        if leave_game_button:
            st.session_state['leave_game_button'] = True 

    if st.session_state['leave_game_button']:
        st.warning("Are you sure you want to leave the game?")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, I'm sure", key="yes_button"):
                leave_game(st.session_state["game_name"],st.session_state["username"])
                st.session_state['leave_game_button'] = False
                st.rerun() 
        
        with col2:
            if st.button("No, cancel", key="no_button"):
                st.session_state['leave_game_button'] = False
                st.rerun()  # To reset the UI cleanly

    log_out = st.button("Log out")  

    if log_out:
        st.session_state["loggedIn"] = False
        st.rerun()
        
        
    
