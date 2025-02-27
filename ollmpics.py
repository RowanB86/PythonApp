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

selected_model = st.selectbox("Select model", options=["Llama-2-7b-chat-hf","zephyr-7b-beta","Mistral-7B-Instruct-v0.2"])
HF_API_TOKEN = st.secrets["HF_API_TOKEN"]


models = {"Llama-2-7b-chat-hf":"meta-llama/Llama-2-7b-chat-hf",
           "zephyr-7b-beta":"HuggingFaceH4/zephyr-7b-beta",
         "Mistral-7B-Instruct-v0.2": "mistralai/Mistral-7B-Instruct-v0.2"}


model_descriptions = {"Llama-2-7b-chat-hf": """
    <div style="background-color:#f4f4f4; padding:15px; border-radius:10px;">
        <h2 style="color:#4A90E2;">🦙 LLaMA 2 - 7B Chat Model</h2>
        
        <h3 style="color:#2C3E50;">🛠 Model Overview</h3>
        <ul>
            <li><strong>🧠 Parameter Count:</strong> 7 Billion</li>
            <li><strong>⚙️ Architecture:</strong> Optimized Transformer</li>
            <li><strong>📚 Training Data:</strong> 2 Trillion Tokens from Publicly Available Online Sources</li>
            <li><strong>🔧 Fine-Tuning:</strong> SFT + RLHF for Dialogue Optimization</li>
        </ul>
        
        <h3 style="color:#2C3E50;">🚀 Performance Highlights</h3>
        <ul>
            <li>✅ Outperforms many open-source chat models on key benchmarks</li>
            <li>✅ Comparable in helpfulness and safety to closed-source models like ChatGPT</li>
        </ul>

        <h3 style="color:#2C3E50;">🔍 Usage Details</h3>
        <ul>
            <li><strong>✍️ Input:</strong> Text Prompts</li>
            <li><strong>📝 Output:</strong> AI-generated Responses</li>
            <li><strong>📏 Context Window:</strong> Supports up to 4,000 Tokens</li>
            <li><strong>📜 Prompt Formatting:</strong> Use the following format for best results:
                <pre style="background-color:#EAECEE; padding:10px; border-radius:5px;">
&lt;s&gt;[INST] &lt;&lt;SYS&gt;&gt;
Your system prompt here
&lt;&lt;/SYS&gt;&gt;

User Input [/INST]
                </pre>
            </li>
        </ul>

        <h3 style="color:#2C3E50;">📜 Licensing & Access</h3>
        <ul>
            <li>🔐 Licensed under Meta's Custom Commercial License</li>
            <li>🌐 Accept license terms on the official Meta website</li>
            <li>📄 More details: <a href='https://huggingface.co/meta-llama/Llama-2-7b-chat-hf' target='_blank'>Hugging Face Model Page</a></li>
        </ul>
    </div>
    """,
"zephyr-7b-beta": """
    <div style="background-color:#f4f4f4; padding:15px; border-radius:10px;">
        <h2 style="color:#4A90E2;">🪁 Zephyr-7B-Beta</h2>

        <h3 style="color:#2C3E50;">🛠 Model Overview</h3>
        <ul>
            <li><strong>🧠 Parameter Count:</strong> 7 Billion</li>
            <li><strong>⚙️ Architecture:</strong> Transformer-based</li>
            <li><strong>📚 Training Data:</strong> Extensive Public Text Datasets</li>
            <li><strong>🔧 Fine-Tuning:</strong> dDPO (Direct Preference Optimization) for Better Response Alignment</li>
        </ul>

        <h3 style="color:#2C3E50;">🚀 Performance Highlights</h3>
        <ul>
            <li>✅ Strong alignment with user queries</li>
            <li>✅ Optimized for helpfulness and reduced biases</li>
            <li>✅ Outperforms many models in real-world conversational tasks</li>
        </ul>

        <h3 style="color:#2C3E50;">🔍 Usage Details</h3>
        <ul>
            <li><strong>✍️ Input:</strong> Text Prompts</li>
            <li><strong>📝 Output:</strong> AI-generated Responses</li>
            <li><strong>📏 Context Window:</strong> Supports up to 4,000 Tokens</li>
            <li><strong>📜 Prompt Formatting:</strong> Uses standard text input without special formatting.</li>
        </ul>

        <h3 style="color:#2C3E50;">⚙️ Adjustable Parameters</h3>
        <ul>
            <li><strong>🔥 Temperature:</strong> Controls randomness (Higher = More creative, Lower = More deterministic)</li>
            <li><strong>🎯 Top-P Sampling:</strong> Restricts output choices to the most probable subset</li>
            <li><strong>🔄 Repetition Penalty:</strong> Reduces redundancy in responses</li>
            <li><strong>📝 Max Tokens:</strong> Limits the number of generated tokens in the response</li>
        </ul>

        <h3 style="color:#2C3E50;">📜 Licensing & Access</h3>
        <ul>
            <li>🔐 Open-weight model under Apache 2.0 License</li>
            <li>🌐 Available for both research and commercial use</li>
            <li>📄 More details: <a href='https://huggingface.co/HuggingFaceH4/zephyr-7b-beta' target='_blank'>Hugging Face Model Page</a></li>
        </ul>
    </div>
    """,

"Mistral-7B-Instruct-v0.2": """
    <div style="background-color:#f4f4f4; padding:15px; border-radius:10px;">
        <h2 style="color:#4A90E2;">🌪️ Mistral-7B-Instruct-v0.2</h2>

        <h3 style="color:#2C3E50;">🛠 Model Overview</h3>
        <ul>
            <li><strong>🧠 Parameter Count:</strong> 7 Billion</li>
            <li><strong>⚙️ Architecture:</strong> Transformer-based</li>
            <li><strong>📚 Training Data:</strong> Web data + Publicly available sources</li>
            <li><strong>🔧 Fine-Tuning:</strong> Optimized for Instruction-Based Tasks</li>
        </ul>

        <h3 style="color:#2C3E50;">🚀 Performance Highlights</h3>
        <ul>
            <li>✅ Optimized for Instruction Following</li>
            <li>✅ Capable of Multi-Turn Conversations</li>
            <li>✅ Strong Performance Across Diverse NLP Tasks</li>
            <li>✅ Improved Prompt Adherence Over Previous Versions</li>
        </ul>

        <h3 style="color:#2C3E50;">🔍 Usage Details</h3>
        <ul>
            <li><strong>✍️ Input:</strong> Text Prompts</li>
            <li><strong>📝 Output:</strong> AI-generated Responses</li>
            <li><strong>📏 Context Window:</strong> Supports up to 4,096 Tokens</li>
            <li><strong>📜 Prompt Formatting:</strong> Standard conversational input/output</li>
        </ul>

        <h3 style="color:#2C3E50;">⚙️ Adjustable Parameters</h3>
        <ul>
            <li><strong>🔥 Temperature:</strong> Controls randomness (Higher = More creative, Lower = More deterministic)</li>
            <li><strong>🎯 Top-P Sampling:</strong> Restricts output choices to the most probable subset</li>
            <li><strong>🔄 Repetition Penalty:</strong> Reduces redundancy in responses</li>
            <li><strong>📝 Max Tokens:</strong> Limits the number of generated tokens in the response</li>
        </ul>

        <h3 style="color:#2C3E50;">📜 Licensing & Access</h3>
        <ul>
            <li>🔐 Open-weight model under Apache 2.0 License</li>
            <li>🌐 Available for research & commercial use</li>
            <li>📄 More details: <a href='https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2' target='_blank'>Hugging Face Model Page</a></li>
        </ul>
    </div>
    """

                     }

with st.expander("Model Descriptions"):
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
