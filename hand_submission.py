import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
import json

firebase_credentials = json.loads(st.secrets["firebase"]["service_account_json"])
cred = credentials.Certificate(firebase_credentials)

# Initialize Firebase (only once)
if not firebase_admin._apps:
    # Initialize Firebase
    initialize_app(cred, {
        'databaseURL': 'https://pokerhandsubmission-default-rtdb.europe-west1.firebasedatabase.app/'
    })





# Get Firestore database instance
db = firestore.client()

# Define a fixed document ID (this will be overwritten each time)
DOC_ID = "current_hole_cards"

# Streamlit UI
st.title("♠️ Submit Hole Cards to Firebase (Overwrite Mode)")
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
