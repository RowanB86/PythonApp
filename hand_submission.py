import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
import json
import pandas as pd
import openai

# Load Firebase credentials from Streamlit secrets
firebase_credentials = json.loads(st.secrets["firebase"]["service_account_json"])
cred = credentials.Certificate(firebase_credentials)

# Initialize Firebase (only once)
if not firebase_admin._apps:
    initialize_app(cred, {
        'databaseURL': 'https://pokerhandsubmission-default-rtdb.europe-west1.firebasedatabase.app/'
    })

# Get Firestore database instance
db = firestore.client()

# Define a fixed document ID for hole cards
DOC_ID = "current_hole_cards"


openai.api_key = st.secrets["openai"]["api_key"]

# Streamlit UI
st.title("♠️ Poker AI Assistant")
st.write("Enter your hole cards and submit to Firebase. This will overwrite the last submission.")

# Input: Hole Cards
hole_cards = st.text_input("Enter Your Hole Cards (e.g., '8s 8d')")

# Submit button
if st.button("Submit Hole Cards"):
    if hole_cards:
        # Save (overwrite the same document)
        db.collection("hole_cards").document(DOC_ID).set({"hole_cards": hole_cards})
        st.success(f"✅ Hole cards '{hole_cards}' submitted successfully and overwritten!")
    else:
        st.warning("⚠️ Please enter your hole cards before submitting.")

# **New Section: Analyze Player Stats**
st.header("📊 Analyze Player Stats")

if st.button("Analyze Player Stats"):
    # Retrieve player stats from Firestore
    stats_doc = db.collection("player_stats").document("latest_stats").get()

    if stats_doc.exists:
        stats_data = stats_doc.to_dict()["stats"]
        df_stats = pd.DataFrame(stats_data)

        # Display DataFrame
        st.subheader("📋 Player Statistics")
        st.dataframe(df_stats)

        # Generate player analysis summaries
        st.subheader("🧐 Player Analysis & Strategy")
        
        player_summaries = []
        for _, row in df_stats.iterrows():
            player_name = row["player_name"]
            vpip = row["vpip"]
            pfr = row["pfr"]
            three_bet = row["3-Bet %"]

            # Construct prompt for OpenAI analysis
            prompt = f"""
            You are a poker AI. Analyze the player's stats and give a **concise** playing style summary. Then, suggest the **best strategy** to exploit them.

            **Player Name:** {player_name}
            **VPIP (Voluntarily Put Money In Pot %):** {vpip}
            **PFR (Preflop Raise %):** {pfr}
            **3-Bet %:** {three_bet}

            **Output format:** 
            - **Playing Style:** (briefly describe their tendencies)
            - **Strategy to Play Against Them:** (how to adjust play to exploit them)
            """
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}]
                )

            except openai.error.AuthenticationError as e:
                st.error(f"OpenAI Authentication Error: {e}")
            except Exception as e:
                st.error(f"Unexpected Error: {e}")
            summary = response.choices[0].message.content

            player_summaries.append(f"**{player_name}**\n{summary}\n")

        # Display player summaries
        for summary in player_summaries:
            st.markdown(summary)

    else:
        st.warning("⚠️ No player stats found in Firestore.")
