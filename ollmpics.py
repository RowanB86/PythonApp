import streamlit as st
import boto3
import os
from ctransformers import AutoModelForCausalLM

# AWS S3 Configuration (Set these in Streamlit Secrets)
S3_BUCKET = st.secrets["S3_BUCKET"]
S3_MODEL_KEY = st.secrets["S3_MODEL_KEY"]

models = {
    "Mistral Instruct": "mistral-7b-instruct-v0.1.Q4_0.gguf"
}

model_descriptions = {
    "Mistral Instruct": """
- Fast Responses
- Trained by Mistral AI   
- Uncensored 
- Licensed for commercial use                               
---
                                                  
**📌 Specifications:**  
- **📁 File size:** 3.83 GB  
- **💾 RAM required:** 8 GB  
- **🔢 Parameters:** 7 billion  
- **🛠 Quantisation:** `q4_0`  
- **🔠 Type:** `Mistral`  
"""
}

# Initialize S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
)


def download_models():
    local_model_path = os.path.join("/tmp", models["Mistral Instruct"])  

    if not os.path.exists(local_model_path):
        with st.spinner(f"Downloading {models['Mistral Instruct']} from S3..."):
            s3.download_file(S3_BUCKET, S3_MODEL_KEY, local_model_path)
        st.success(f"Model {models['Mistral Instruct']} downloaded successfully!")

    # ✅ Debugging: Print file size and confirm it's readable
    if os.path.exists(local_model_path):
        file_size = os.path.getsize(local_model_path) / (1024 * 1024 * 1024)  # Convert bytes to GB
        st.write(f"✅ Model found at: {local_model_path} (Size: {file_size:.2f} GB)")
    else:
        st.error(f"❌ Model file missing after download: {local_model_path}")

    return local_model_path
# Download the model and get its local path
model_path = download_models()

# Streamlit UI
st.title("GPT4All Chatbot")
user_input = st.text_area("Enter your prompt:")

model_list = list(models.keys())

select_model = st.selectbox("Select Model", options=model_list)
model_description = st.empty()

if select_model:
    with st.expander("Model information"):
        model_description.markdown(model_descriptions[select_model])

# ✅ Use the correct local model path
gpt = AutoModelForCausalLM.from_pretrained(
    model_path,  # ✅ Load the model from /tmp/
    model_type="auto"
)

st.session_state["query"] = st.text_input("Enter query")
st.session_state["max_tokens"] = st.text_input("Enter token limit (including input and output):")
st.session_state["temp"] = st.text_input("Enter temperature (the higher the temperature, the more diverse the response):")
st.session_state["top_p"] = st.text_input("Enter top-p sampling (controls how many words are considered before choosing one):")
st.session_state["repeat_penalty"] = st.text_input("Enter repeat penalty (higher values reduce repetition):")

assess_bid = st.button("Submit query")

if assess_bid:
    prompt = f"""
    <|im_start|>system
    You are an AI specializing in quick, efficient responses. :
    <|im_end|>

    <|im_start|>user
    {st.session_state["query"]}
    <|im_end|>

    <|im_start|>assistant
    """

    # Generate Response
    response = gpt.generate(
        prompt,
        max_tokens=int(st.session_state["max_tokens"]),
        temp=float(st.session_state["temp"]),
        top_p=float(st.session_state["top_p"]),
        repeat_penalty=float(st.session_state["repeat_penalty"])
    )
    
    st.write("\n\nResponse:")
    st.write(response)
