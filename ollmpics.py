import streamlit as st
from transformers import AutoModelForCausalLM, LlamaTokenizer
import torch

# Set the model name (Change if needed)
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.1-GGUF" # ✅ Load from Hugging Face
HF_TOKEN = st.secrets["HF_TOKEN"] 

# Load tokenizer & model
@st.cache_resource  # Cache the model so it doesn't reload every time
def load_model():
    st.write("🔄 Loading Mistral model from Hugging Face...")
    tokenizer = LlamaTokenizer.from_pretrained(MODEL_NAME, use_auth_token=HF_TOKEN)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,  # ✅ Use float16 to save memory
        device_map="auto",  # ✅ Automatically use GPU if available
        use_auth_token=HF_TOKEN
    )
    st.success("✅ Model loaded successfully!")
    return tokenizer, model

tokenizer, model = load_model()

# Streamlit UI
st.title("Mistral Chatbot")
user_input = st.text_area("Enter your prompt:")

if st.button("Generate Response"):
    with st.spinner("Generating response..."):
        input_ids = tokenizer(user_input, return_tensors="pt").input_ids.to("cuda" if torch.cuda.is_available() else "cpu")

        output = model.generate(input_ids, max_new_tokens=100)
        response_text = tokenizer.decode(output[0], skip_special_tokens=True)

        st.success("Response:")
        st.write(response_text)
