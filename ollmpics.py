import streamlit as st
import requests

# Hugging Face API Key
HF_API_TOKEN = st.secrets["HF_TOKEN"]
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.1"

# Streamlit UI
st.title("Mistral Chatbot")

user_input = st.text_area("Enter your prompt:")

if st.button("Generate Response"):
    with st.spinner("Generating response..."):
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{MODEL_NAME}",
            headers={"Authorization": f"Bearer {HF_API_TOKEN}"},
            json={"inputs": user_input},
        )

        if response.status_code == 200:
            st.success("Response:")
            st.write(response.json()[0]["generated_text"])
        else:
            st.error("Error calling Hugging Face API.")
