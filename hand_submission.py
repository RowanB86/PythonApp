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

                # Display stats
                st.subheader(f"📋 Tournament Player Statistics (Table {latest_table_id})")
                st.dataframe(df_stats)

                # AI analysis
    # AI analysis
    st.subheader("🧐 Player Analysis & Strategy")
    
    player_summaries = []
    for _, row in df_stats.iterrows():
        player_name = row["player_name"]
        total_hands = row.get("total_hands", "N/A")
        vpip = row.get("vpip", "N/A")
        pfr = row.get("pfr", "N/A")
        call_pfr = row.get("Call PFR %", "N/A")
        three_bet = row.get("3-Bet %", "N/A")
        flop_aggression = row.get("Flop Aggression %", "N/A")
        turn_aggression = row.get("Turn Aggression %", "N/A")
        river_aggression = row.get("River Aggression %", "N/A")
        aggression_factor = row.get("aggression_factor", "N/A")
        flop_seen = row.get("Flop Seen %", "N/A")
        wtsd = row.get("WTSD %", "N/A")
        fold_to_cbet = row.get("Fold to C-Bet %", "N/A")
        cbet = row.get("C-Bet %", "N/A")
        fold_to_pfr = row.get("Fold to PFR %", "N/A")
    
        # **Updated AI prompt with all stats**
        prompt = f"""
        You are a poker AI analyzing **tournament** player tendencies.
        Provide a **concise** summary of their playing style and a **strategy** to exploit them.
    
        **Player Name:** {player_name}
        **Total Hands Played:** {total_hands}
        **VPIP (Voluntarily Put Money In Pot %):** {vpip}
        **PFR (Preflop Raise %):** {pfr}
        **Call PFR %:** {call_pfr}
        **3-Bet %:** {three_bet}
        **Flop Aggression %:** {flop_aggression}
        **Turn Aggression %:** {turn_aggression}
        **River Aggression %:** {river_aggression}
        **Aggression Factor:** {aggression_factor}
        **Flop Seen %:** {flop_seen}
        **WTSD (Went to Showdown %):** {wtsd}
        **Fold to C-Bet %:** {fold_to_cbet}
        **C-Bet %:** {cbet}
        **Fold to PFR %:** {fold_to_pfr}
    
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
