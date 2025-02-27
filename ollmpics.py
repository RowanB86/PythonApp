# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 12:27:10 2025

@author: RowanBarua
"""

import streamlit as st
import requests
import json

# Streamlit app layout
st.title("O-LLM-PICS")

selected_model = st.selectbox("Select model", options=["Llama-2-7b-chat-hf","zephyr-7b-beta","Mistral-7B-Instruct-v0.2","Gemma-7B-IT"])
HF_API_TOKEN = st.secrets["HF_API_TOKEN"]


models = {"Llama-2-7b-chat-hf":"meta-llama/Llama-2-7b-chat-hf",
           "zephyr-7b-beta":"HuggingFaceH4/zephyr-7b-beta",
         "Mistral-7B-Instruct-v0.2": "mistralai/Mistral-7B-Instruct-v0.2",
         "GritLM-7B":"GritLM/GritLM-7B",
         "Gemma-7B-IT":"google/gemma-1.1-7b-it",
         "TinyLlama-1.1B-Chat-v1.0","TinyLlama/TinyLlama-1.1B-Chat-v1.0"}


model_descriptions = {
    "Llama-2-7b-chat-hf": """
    ### 🦙 LLaMA 2 - 7B Chat Model

    **🛠 Model Overview**  
    - 🧠 **Parameter Count:** 7 Billion  
    - ⚙️ **Architecture:** Optimized Transformer  
    - 📚 **Training Data:** 2 Trillion Tokens from Publicly Available Online Sources  
    - 🔧 **Fine-Tuning:** SFT + RLHF for Dialogue Optimization  

    **🚀 Performance Highlights**  
    - ✅ Outperforms many open-source chat models on key benchmarks  
    - ✅ Comparable in helpfulness and safety to closed-source models like ChatGPT  

    **🔍 Usage Details**  
    - ✍️ **Input:** Text Prompts  
    - 📝 **Output:** AI-generated Responses  
    - 📏 **Context Window:** Supports up to **4,000 Tokens**  
    - 📜 **Prompt Formatting:** Use the following format for best results:  

    ```plaintext
    <s>[INST] <<SYS>>
    Your system prompt here
    <</SYS>>

    User Input [/INST]
    ```
    
    **📜 Licensing & Access**  
    - 🔐 Licensed under **Meta's Custom Commercial License**  
    - 🌐 Accept license terms on the official Meta website  
    - 📄 [More details on Hugging Face](https://huggingface.co/meta-llama/Llama-2-7b-chat-hf)  
    """,

    "zephyr-7b-beta": """
    ### 🪁 Zephyr-7B-Beta  

    **🛠 Model Overview**  
    - 🧠 **Parameter Count:** 7 Billion  
    - ⚙️ **Architecture:** Transformer-based  
    - 📚 **Training Data:** Extensive Public Text Datasets  
    - 🔧 **Fine-Tuning:** dDPO (Direct Preference Optimization)  

    **🚀 Performance Highlights**  
    - ✅ Strong alignment with user queries  
    - ✅ Optimized for helpfulness and reduced biases  
    - ✅ Outperforms many models in real-world conversational tasks  

    **🔍 Usage Details**  
    - ✍️ **Input:** Text Prompts  
    - 📝 **Output:** AI-generated Responses  
    - 📏 **Context Window:** Supports up to **4,000 Tokens**  
    - 📜 **Prompt Formatting:** Standard text input without special formatting.  

    **⚙️ Adjustable Parameters**  
    - 🔥 **Temperature:** Controls randomness (Higher = More creative, Lower = More deterministic)  
    - 🎯 **Top-P Sampling:** Restricts output choices to the most probable subset  
    - 🔄 **Repetition Penalty:** Reduces redundancy in responses  
    - 📝 **Max Tokens:** Limits the number of generated tokens in the response  

    **📜 Licensing & Access**  
    - 🔐 Open-weight model under **Apache 2.0 License**  
    - 🌐 Available for both research and commercial use  
    - 📄 [More details on Hugging Face](https://huggingface.co/HuggingFaceH4/zephyr-7b-beta)  
    """,

    "Mistral-7B-Instruct-v0.2": """
    ### 🌪️ Mistral-7B-Instruct-v0.2  

    **🛠 Model Overview**  
    - 🧠 **Parameter Count:** 7 Billion  
    - ⚙️ **Architecture:** Transformer-based  
    - 📚 **Training Data:** Web data + Publicly available sources  
    - 🔧 **Fine-Tuning:** Optimized for Instruction-Based Tasks  

    **🚀 Performance Highlights**  
    - ✅ Optimized for Instruction Following  
    - ✅ Capable of Multi-Turn Conversations  
    - ✅ Strong Performance Across Diverse NLP Tasks  
    - ✅ Improved Prompt Adherence Over Previous Versions  

    **🔍 Usage Details**  
    - ✍️ **Input:** Text Prompts  
    - 📝 **Output:** AI-generated Responses  
    - 📏 **Context Window:** Supports up to **4,096 Tokens**  
    - 📜 **Prompt Formatting:** Standard conversational input/output  

    **⚙️ Adjustable Parameters**  
    - 🔥 **Temperature:** Controls randomness (Higher = More creative, Lower = More deterministic)  
    - 🎯 **Top-P Sampling:** Restricts output choices to the most probable subset  
    - 🔄 **Repetition Penalty:** Reduces redundancy in responses  
    - 📝 **Max Tokens:** Limits the number of generated tokens in the response  

    **📜 Licensing & Access**  
    - 🔐 Open-weight model under **Apache 2.0 License**  
    - 🌐 Available for research & commercial use  
    - 📄 [More details on Hugging Face](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2)  
    """,
"Gemma-7B-IT": """
### 💎 Gemma-7B-IT  

**🛠 Model Overview**  
- 🧠 **Parameter Count:** 7 Billion  
- ⚙️ **Architecture:** Transformer-based (Optimized for Instruction-Tuning)  
- 📚 **Training Data:** High-quality dataset including publicly available web data  
- 🔧 **Fine-Tuning:** Specialized for instruction-following tasks (IT = Instruction-Tuned)  

**🚀 Performance Highlights**  
- ✅ **Instruction-Tuned:** Designed to follow human-like instructions accurately  
- ✅ **Improved Coherence:** More structured and logical responses compared to base models  
- ✅ **Multi-Turn Conversations:** Handles follow-ups and maintains context well  
- ✅ **Optimized for Safety & Bias Reduction**  

**🔍 Usage Details**  
- ✍️ **Input:** Text Prompts (Instruction-based queries work best)  
- 📝 **Output:** AI-generated structured responses  
- 📏 **Context Window:** Supports up to **4,096 Tokens**  
- 📜 **Prompt Formatting:** Works best with explicit instructions. Example:

```plaintext
[INST] You are a helpful AI assistant. Explain the importance of data privacy in 100 words. [/INST]
⚙️ Adjustable Parameters

🔥 Temperature: Controls randomness (Higher = More creative, Lower = More deterministic)
🎯 Top-P Sampling: Limits response choices to the most probable subset
🔄 Repetition Penalty: Reduces redundancy in generated text
📝 Max Tokens: Restricts response length
📜 Licensing & Access

🔐 Open-weight model under Apache 2.0 License
🌐 Available for both research and commercial applications
📄 More details on Hugging Face
""",
"TinyLlama-1.1B-Chat-v1.0": """
### 🦙 TinyLlama-1.1B-Chat-v1.0  

**🛠 Model Overview**  
- 🧠 **Parameter Count:** 1.1 Billion  
- ⚙️ **Architecture:** Lightweight Transformer (Optimized for Speed & Low-Compute Use)  
- 📚 **Training Data:** Web-based datasets & instruction-tuned dialogues  
- 🔧 **Fine-Tuning:** Optimized for **chat applications and lightweight NLP tasks**  

**🚀 Performance Highlights**  
- ✅ **Ultra Lightweight:** **Only 1.1B parameters**, making it **efficient for low-resource environments**  
- ✅ **Fast Inference:** Runs well on **CPUs and low-end GPUs**  
- ✅ **Optimized for Conversational AI:** Handles **short & structured** conversations effectively  
- ✅ **Low Memory Usage:** Suitable for **edge devices, mobile, and embedded applications**  

**🔍 Usage Details**  
- ✍️ **Input:** Text prompts (Works best for short, structured queries)  
- 📝 **Output:** AI-generated responses  
- 📏 **Context Window:** Supports **up to 2,048 Tokens**  
- 📜 **Prompt Formatting:** Standard format, simple Q&A structure. Example:

```plaintext
User: What is the capital of France?  
Assistant: The capital of France is Paris.
⚙️ Adjustable Parameters

🔥 Temperature: Controls randomness (Higher = More creative, Lower = More deterministic)
🎯 Top-P Sampling: Limits response choices to the most probable subset
🔄 Repetition Penalty: Reduces redundancy in responses
📝 Max Tokens: Limits response length
📜 Licensing & Access

🔐 Open-weight model under Apache 2.0 License
🌐 Available for both research and commercial applications
📄 More details on Hugging Face
"""

}


with st.expander("Model Description"):
           try:
                      st.markdown(model_descriptions[selected_model]  ,unsafe_allow_html=True)  
           except:
                      pass



prompt = st.text_area("Enter prompt:") 

st.session_state["temp"] = st.text_input("Enter temperature (the higher the temperature the more diverse and creative the response):",value=0.7)
st.session_state["top_p"]  = st.text_input("Enter top-p sampling (Controls how many words are considered before choosing one):",value=0.9)
st.session_state["repeat_penalty"]  = st.text_input("Enter repeat penalty (the higher this is, the more aggressively the model avoids repetition):",value=1.1)
st.session_state["max_tokens"] = st.text_input("Enter token limit (including input and output):",value=800)

if st.button("Submit Query"):
    MODEL_PATH = models[selected_model]


    

    api_url =  f"https://api-inference.huggingface.co/models/{MODEL_PATH}"
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "inputs": prompt,
        "parameters": {
                        "max_new_tokens": int(st.session_state["max_tokens"]) ,       # Controls the response length
                        "temperature": float(st.session_state["temp"]) ,          # Higher = more random, Lower = more predictable
                        "top_p": float(st.session_state["top_p"]),                # Nucleus sampling (controls diversity)
                        "repetition_penalty": float(st.session_state["repeat_penalty"])    # Penalizes repeating phrases
                    }
    })
    
    
    response = requests.post(api_url, headers=headers, data=data)
    
    if response.status_code == 200:
        st.write("Response:")
        
        response_data = response.json()
        if isinstance(response_data, list) and len(response_data) > 0:
            generated_text = response_data[0].get("generated_text", "").strip()
            if "[/INST]" in generated_text:
                generated_text = generated_text.split("[/INST]", 1)[-1].strip()  # Remove prompt from response

            # Format output with markdown
            st.subheader("💡 Generated Response:")
            st.markdown(
                f'<div style="background-color:#f4f4f4; padding:10px; border-radius:5px;">'
                f'<p style="font-size:16px;">{generated_text}</p>'
                f'</div>',
                unsafe_allow_html=True
            )
    else:
        st.error(f"Error {response.status_code}: {response.text}")
