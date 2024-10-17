# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 21:01:42 2024

@author: RowanBarua
"""

from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import torch
import streamlit as st
import fitz
from torch.nn.functional import softmax

# Load fine-tuned model for question answering
tokenizer = AutoTokenizer.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")
model = AutoModelForQuestionAnswering.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")

st.title('BERT Question Answering App')

# Input text and question
context = st.text_area("Context", "")
question = st.text_input("Question", "")
prob_tolerance = float(st.text_input("Set Minimum Answer Probability","0.20"))

if st.button("Get Answer"):
    
    question_tokens = tokenizer(question, return_tensors='pt')
    
    
    # Tokenize inputs
    inputs = tokenizer(context, return_tensors='pt')
    # Assume cls_token_id and sep_token_id are retrieved from the tokenizer
    # Get the token IDs for the special tokens
    cls_token_id = tokenizer.cls_token_id
    sep_token_id = tokenizer.sep_token_id
    cls_token = torch.tensor([[cls_token_id]], dtype=torch.long)
    sep_token = torch.tensor([[sep_token_id]], dtype=torch.long)
    
    # Concatenate to create the complete input_ids
    #input_ids_with_special_tokens = torch.cat([cls_token, question_tokens['input_ids'], sep_token, chunk, sep_token], dim=1)
    
    # Similarly, modify the attention mask
    cls_attention_mask = torch.tensor([[1]], dtype=torch.long)  # Attention mask for [CLS] token
    sep_attention_mask = torch.tensor([[1]], dtype=torch.long)  # Attention mask for [SEP] token
    
    num_tokens = inputs['input_ids'].shape[1]
    
    chunks = []
    next_token = 0
    
    while True:
        last_token = min(num_tokens-1,next_token+480)
        chunks.append(inputs['input_ids'][:,next_token:last_token+1])
        
        if last_token == num_tokens - 1:
            break
    
    
        next_token += 240
    
    for i in range(0,len(chunks)):
    # Run the model
        
        chunk = chunks[i]
        context_attention_mask = torch.ones_like(chunk)  # Attention mask for the context
        
        inputs = {
            'input_ids': torch.cat([cls_token,question_tokens['input_ids'],sep_token, chunk,sep_token], dim=1),
            'attention_mask': torch.cat([cls_attention_mask,question_tokens['attention_mask'],sep_attention_mask,context_attention_mask,sep_attention_mask], dim=1)
        }
        
    
        outputs = model(**inputs)
        
        # Sort start and end logits for multiple spans
        start_logits = outputs.start_logits
        end_logits = outputs.end_logits
        
        # Apply softmax to get the probabilities
        start_probs = softmax(start_logits, dim=-1)
        end_probs = softmax(end_logits, dim=-1)
        
        # Get the top N start and end indices with the highest probabilities
        N = 12  # Number of spans to capture
        top_start_indices = torch.topk(start_logits, N).indices.squeeze()
        top_end_indices = torch.topk(end_logits, N).indices.squeeze()
        
        min_index = -1
        max_index = -1
        
        answers = []
        answer_list = []
        
        for start_index, end_index in zip(top_start_indices, top_end_indices):
            if end_index >= start_index:  # Valid span
                if end_index <= min_index or max_index <= start_index:
                    
                    start_prob = start_probs[0][start_index].item()
                    end_prob = end_probs[0][end_index].item()
                   
                    # Calculate the combined probability as the product of start and end probabilities
                    answer_prob = start_prob * end_prob
                    # Calculate the combined probability as 
            
                    answer_tokens = inputs["input_ids"][0][start_index: end_index+1]
                    answer = tokenizer.decode(answer_tokens, skip_special_tokens=True)
                    
                    if answer_prob > prob_tolerance and answer.strip() and answer not in answer_list:
                        answers.append((answer,answer_prob))
                        answer_list.append(answer)
                    
                    if start_index >= min_index:
                        min_index = start_index
                    
                    if end_index >= max_index:
                        max_index = end_index
                        
        # Print all captured answers
        for idx, (answer, prob) in enumerate(answers):
            st.write(f"Answer: {answer} (Probability: {prob:.4f})")


