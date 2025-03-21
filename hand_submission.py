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

                # Display stats (including WTSD% and Fold to C-Bet % if present)
                st.subheader(f"📋 Tournament Player Statistics (Table {latest_table_id})")
                st.dataframe(df_stats)

                # AI analysis
                st.subheader("🧐 Player Analysis & Strategy")

                player_summaries = []
                for _, row in df_stats.iterrows():
                    player_name = row["player_name"]
                    vpip = row.get("vpip", "N/A")
                    pfr = row.get("pfr", "N/A")
                    three_bet = row.get("3-Bet %", "N/A")
                    call_pfr = row.get("Call PFR %", "N/A")
                    flop_seen = row.get("Flop Seen %", "N/A")
                    wtsd = row.get("WTSD %", "N/A")
                    fold_to_cbet = row.get("Fold to C-Bet %", "N/A")

                    # Updated AI prompt with new metrics
                    prompt = f"""
                    You are a poker AI analyzing **tournament** player tendencies.
                    Provide a **concise** summary of their playing style and a **strategy** to exploit them.

                    **Player Name:** {player_name}
                    **VPIP (Voluntarily Put Money In Pot %):** {vpip}
                    **PFR (Preflop Raise %):** {pfr}
                    **3-Bet %:** {three_bet}
                    **Call PFR %:** {call_pfr}
                    **Flop Seen %:** {flop_seen}
                    **WTSD (Went to Showdown %):** {wtsd}
                    **Fold to C-Bet %:** {fold_to_cbet}

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

                for summary in player_summaries:
                    st.markdown(summary)
            else:
                st.warning(f"⚠️ No player stats found for **Table {latest_table_id}** in Firestore.")
        else:
            st.warning("⚠️ No recent tournament table ID found.")
    else:
        st.warning("⚠️ Tournament metadata not available in Firestore.")
