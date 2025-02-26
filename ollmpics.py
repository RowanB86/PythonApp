import streamlit as st
import boto3
import os
from gpt4all import GPT4All

# AWS S3 Configuration (Set these in Streamlit Secrets)
S3_BUCKET = st.secrets["S3_BUCKET"]
S3_MODEL_KEY = st.secrets["S3_MODEL_KEY"]
LOCAL_MODEL_PATH = "gpt4all-model.gguf"

# Initialize S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
)

# Function to download the model from S3 if not present
def download_model():
    if not os.path.exists(LOCAL_MODEL_PATH):
        with st.spinner("Downloading model from S3..."):
            s3.download_file(S3_BUCKET, S3_MODEL_KEY, LOCAL_MODEL_PATH)
        st.success("Model downloaded successfully!")

# Download model at startup
download_model()

# Load GPT4All model
st.spinner("Loading the GPT4All model...")
model = GPT4All(LOCAL_MODEL_PATH)
st.success("Model loaded!")

# Streamlit UI
st.title("GPT4All Chatbot")
user_input = st.text_area("Enter your prompt:")

if st.button("Generate"):
    with st.spinner("Generating response..."):
        output = model.generate(user_input, max_tokens=100)
        st.success(output)
