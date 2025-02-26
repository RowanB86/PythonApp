import streamlit as st
import boto3
import os
from gpt4all import GPT4All

# AWS S3 Configuration (Set these in Streamlit Secrets)
S3_BUCKET = st.secrets["S3_BUCKET"]
S3_MODEL_KEY = st.secrets["S3_MODEL_KEY"]
LOCAL_MODEL_PATH = "qwen2.5-coder-7b-instruct-q4_0.gguf"

models = {
    
"Reasoner v1":   "qwen2.5-coder-7b-instruct-q4_0.gguf",

"Mistral Instruct": "mistral-7b-instruct-v0.1.Q4_0.gguf",
          
"GPT4All Falcon": "gpt4all-falcon-newbpe-q4_0.gguf",
          
"Wizard v1.2": "wizardlm-13b-v1.2.Q4_0.gguf",
          
"Hermes": "nous-hermes-llama2-13b.Q4_0.gguf"
          
 }

model_descriptions = {"Reasoner v1": """
- Based on Owen2.5-Coder 7B 
- Built-in JavaScript code interpreter   
- Complex reasoning tasks aided by computation analysis  
- Apache License Version 2.0  
- #reasoning`  
                                            
---
                                                
**📌 Specifications:**  
- **📁 File size:** 4.13 GB  
- **💾 RAM required:** 8 GB  
- **🔢 Parameters:** 8 billion  
- **🛠 Quantisation:** `q4_0`  
- **🔠 Type:** `qwen2`  
""",
          
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
""",
    
"GPT4All Falcon": """
- Fast Responses
- Instruction based
- Trained by T2 
- Finetuned by Nomic AI
- Licensed for commercial use                               
---
                                                
**📌 Specifications:**  
- **📁 File size:** 3.92 GB  
- **💾 RAM required:** 8 GB  
- **🔢 Parameters:** 7 billion  
- **🛠 Quantisation:** `q4_0`  
- **🔠 Type:** `Falcon`  
""",
    
          
"Wizard v1.2": """
- Instruction based
- Gives very long responses
- Finetuned with only 1k of high-quality data 
- Trained by Microsoft and Peking University
- Cannot be used commercially                               
---
                                                
**📌 Specifications:**  
- **📁 File size:** 6.86 GB  
- **💾 RAM required:** 16 GB  
- **🔢 Parameters:** 13 billion  
- **🛠 Quantisation:** `q4_0`  
- **🔠 Type:** `LLaMA2`  
""",
          
    
"Hermes": """
- Instruction based
- Gives very long responses
- Curated with 300,000 uncensored instructions
- Trained by Nous Research
- Cannot be used commercially                               
---
                                                
**📌 Specifications:**  
- **📁 File size:** 6.86 GB  
- **💾 RAM required:** 16 GB  
- **🔢 Parameters:** 13 billion  
- **🛠 Quantisation:** `q4_0`  
- **🔠 Type:** `LLaMA2`  
"""            
    

 }

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
