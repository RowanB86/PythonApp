import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
import json
import pandas as pd
import openai

# Load Firebase credentials from Streamlit secrets
firebase_credentials = json.loads(st.secrets["firebase"]["service_account_json"])
cred = credentials.Certificate(firebase_credentials)

# Initialize Firebase
if not firebase_admin._apps:
    initialize_app(cred, {
        'databaseURL': 'https://pokerhandsubmission-default-rtdb.europe-west1.firebasedatabase.app/'
    })

# Get Firestore DB reference
db = firestore.client()

# Set OpenAI API Key
openai.api_key = st.secrets["openai"]["api_key"]

# UI
st.title("🏆 Poker AI Assistant - Tournament Mode")
st.write("Enter your hole cards and submit to Firebase. This will overwrite the last submission.")

# Submit Hole Cards
hole_cards = st.text_input("Enter Your Hole Cards (e.g., '8s 8d')")
if st.button("Submit Hole Cards"):
    if hole_cards:
        db.collection("hole_cards").document("current_hole_cards").set({"hole_cards": hole_cards})
        st.success(f"✅ Hole cards '{hole_cards}' submitted successfully!")
    else:
        st.warning("⚠️ Please enter your hole cards before submitting.")

# Analyze Tournament Player Stats
st.header("📊 Analyze Tournament Player Stats")

if st.button("Analyze Tournament Players"):
    table_id_doc = db.collection("tournament_metadata").document("latest_table_id").get()
    
    if table_id_doc.exists:
        latest_table_id = table_id_doc.to_dict().get("table_id")

        if latest_table_id:
            stats_doc = db.collection("tournament_player_stats").document(f"table_{latest_table_id}").get()

            if stats_doc.exists:
                stats_data = stats_doc.to_dict()["stats"]
                df_stats = pd.DataFrame(stats_data)

                # **Reorder Columns for Logical Flow**
                column_order = [
                    "player_name", "total_hands",  # General Info
                    "vpip", "pfr", "3-Bet %", "Call PFR %", "Fold to PFR %",  # Preflop
                    "Flop Seen %", "C-Bet %", "Fold to C-Bet %",  # Postflop
                    "Flop Aggression %", "Turn Aggression %", "River Aggression %", "aggression_factor",  # Aggression
                    "WTSD %"  # Showdown
                ]
                
                # Select columns in defined order if they exist in DataFrame
                df_stats = df_stats[[col for col in column_order if col in df_stats.columns]]

                # Display stats
                st.subheader(f"📋 Tournament Player Statistics (Table {latest_table_id})")
                st.dataframe(df_stats)

                # AI analysis
                st.subheader("🧐 Player Analysis & Strategy")

                player_summaries = []
                for _, row in df_stats.iterrows():
                    player_name = row["player_name"]
                    total_hands = row.get("total_hands", "N/A")
                    vpip = row.get("vpip", "N/A")
                    pfr = row.get("pfr", "N/A")
                    three_bet = row.get("3-Bet %", "N/A")
                    call_pfr = row.get("Call PFR %", "N/A")
                    fold_to_pfr = row.get("Fold to PFR %", "N/A")
                    flop_seen = row.get("Flop Seen %", "N/A")
                    cbet = row.get("C-Bet %", "N/A")
                    fold_to_cbet = row.get("Fold to C-Bet %", "N/A")
                    flop_aggression = row.get("Flop Aggression %", "N/A")
                    turn_aggression = row.get("Turn Aggression %", "N/A")
                    river_aggression = row.get("River Aggression %", "N/A")
                    aggression_factor = row.get("aggression_factor", "N/A")
                    wtsd = row.get("WTSD %", "N/A")

                    # **Updated AI prompt with all stats**
                    prompt = f"""
                    You are a poker AI analyzing **tournament** player tendencies.
                    Please provide a rapid answer to this question

                    **Player Name:** {player_name}
                    **Total Hands Played:** {total_hands}
                    
                    **Preflop Behavior:**
                    - VPIP (Voluntarily Put Money In Pot %): {vpip}
                    - PFR (Preflop Raise %): {pfr}
                    - 3-Bet %: {three_bet}
                    - Call PFR %: {call_pfr}
                    - Fold to PFR %: {fold_to_pfr}
                    
                    **Postflop Behavior:**
                    - Flop Seen %: {flop_seen}
                    - C-Bet %: {cbet}
                    - Fold to C-Bet %: {fold_to_cbet}
                    
                    **Aggression:**
                    - Flop Aggression %: {flop_aggression}
                    - Turn Aggression %: {turn_aggression}
                    - River Aggression %: {river_aggression}
                    - Aggression Factor: {aggression_factor}
                    
                    **Showdown:**
                    - WTSD (Went to Showdown %): {wtsd}

                    **Output format:** 
                    - **Playing Style:** (briefly describe their tendencies)
                    - **Strategy to Play Against Them:** (how to adjust play to exploit them)
                    """

                    try:
                        response = openai.ChatCompletion.create(
                            model="gpt-4o",
                            messages=[{"role": "user", "content": prompt}]
                        )
                        summary = response.choices[0].message.content
                        player_summaries.append(f"**{player_name}**\n{summary}\n")
                    except Exception as e:
                        st.error(f"Error analyzing {player_name}: {e}")

                # Display AI-generated player summaries
                for summary in player_summaries:
                    st.markdown(summary)

            else:
                st.warning(f"⚠️ No player stats found for **Table {latest_table_id}** in Firestore.")
        else:
            st.warning("⚠️ No recent tournament table ID found.")
    else:
        st.warning("⚠️ Tournament metadata not available in Firestore.")

query = st.text_input("Enter question", key="question")

if st.button("Submit question"):
    table_id_doc = db.collection("tournament_metadata").document("latest_table_id").get()
    if table_id_doc.exists:
        latest_table_id = table_id_doc.to_dict().get("table_id")

        if latest_table_id:
            stats_doc = db.collection("tournament_player_stats").document(f"table_{latest_table_id}").get()

            if stats_doc.exists:
                stats_data = stats_doc.to_dict()["stats"]
                df_stats = pd.DataFrame(stats_data)

                # **Reorder Columns for Logical Flow**
                column_order = [
                    "player_name", "total_hands",  # General Info
                    "vpip", "pfr", "3-Bet %", "Call PFR %", "Fold to PFR %",  # Preflop
                    "Flop Seen %", "C-Bet %", "Fold to C-Bet %",  # Postflop
                    "Flop Aggression %", "Turn Aggression %", "River Aggression %", "aggression_factor",  # Aggression
                    "WTSD %"  # Showdown
                ]
                
                # Select columns in defined order if they exist in DataFrame
                df_stats = df_stats[[col for col in column_order if col in df_stats.columns]]
                stats_string = ''

                player_summaries = []
                for _, row in df_stats.iterrows():
                    player_name = row["player_name"]
                    total_hands = row.get("total_hands", "N/A")
                    vpip = row.get("vpip", "N/A")
                    pfr = row.get("pfr", "N/A")
                    three_bet = row.get("3-Bet %", "N/A")
                    call_pfr = row.get("Call PFR %", "N/A")
                    fold_to_pfr = row.get("Fold to PFR %", "N/A")
                    flop_seen = row.get("Flop Seen %", "N/A")
                    cbet = row.get("C-Bet %", "N/A")
                    fold_to_cbet = row.get("Fold to C-Bet %", "N/A")
                    flop_aggression = row.get("Flop Aggression %", "N/A")
                    turn_aggression = row.get("Turn Aggression %", "N/A")
                    river_aggression = row.get("River Aggression %", "N/A")
                    aggression_factor = row.get("aggression_factor", "N/A")
                    wtsd = row.get("WTSD %", "N/A")

                    # **Updated AI prompt with all stats**
                    stats = f"""



                    **Player Stats:**

                    **Player Name:** {player_name}
                    **Total Hands Played:** {total_hands}
                    
                    **Preflop Behavior:**
                    - VPIP (Voluntarily Put Money In Pot %): {vpip}
                    - PFR (Preflop Raise %): {pfr}
                    - 3-Bet %: {three_bet}
                    - Call PFR %: {call_pfr}
                    - Fold to PFR %: {fold_to_pfr}
                    
                    **Postflop Behavior:**
                    - Flop Seen %: {flop_seen}
                    - C-Bet %: {cbet}
                    - Fold to C-Bet %: {fold_to_cbet}
                    
                    **Aggression:**
                    - Flop Aggression %: {flop_aggression}
                    - Turn Aggression %: {turn_aggression}
                    - River Aggression %: {river_aggression}
                    - Aggression Factor: {aggression_factor}
                    
                    **Showdown:**
                    - WTSD (Went to Showdown %): {wtsd} """

                    stats_string += '\n' + stats

                query_to_AI =  f"""Please provid a rapid answer to assist a live poker player to this question: {query} , 
                       based on these player stats: {stats_string}"""

                
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": query_to_AI}]
                    )
                    summary = response.choices[0].message.content

                    st.write(summary)
                except Exception as e:
                    st.error(f"Error analyzing {player_name}: {e}")    
