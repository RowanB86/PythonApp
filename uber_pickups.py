# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import streamlit as st
import pandas as pd
import numpy as np
from winsound import Beep
from time import sleep
from random import randint

st.title('Uber pickups in NYC')

DATE_COLUMN = 'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
         'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

@st.cache_data
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe.
data = load_data(10000)
# Notify the reader that the data was successfully loaded.
data_load_state.text("Done! (using st.cache_data21)")

def jab():
   freq = 500
   dur = 500
   Beep(freq, dur)
  
def hook():
   freq = 5000
   dur = 1000
   Beep(freq, dur)
  
def Bjab():
   freq = 250
   dur = 750
   Beep(freq, dur)

def Bhook():
   freq = 150
   dur = 1000
   Beep(freq, dur)
  
  
  
x = " lands a Jab!"
y = " lands a Right Hook!!!"

dx = "Blocks Jab"
dy = "Blocks Hook"

rocky = "Rocky\n\n\n\n\n   "
apollo = "Apollo\n\n\n\n\n   "

P1 = 0
P2 = 0


while P1 <= 12 and P2 <= 12:
    if P1 >= 10:
        st.text("ROCKY WINS!!!! ")
        break
    if P2 >= 10:
        st.text("APOLLO WINS!!!! ")
        break
   
   
    ran = randint(1,12)
    chance = randint(1,100)
   
   
    if ran >= 1 and ran <= 4:
        if chance <=33:
            st.text(rocky + x)
            P1 = P1 + 1
            st.text("\nRocky Scores " + str(P1) + " Apollo " + str(P2) + "\n") 
            jab()
            sleep(randint(1,3))
           
        else:
            st.text(apollo + dx)
            st.text("\nRocky Scores " + str(P1) + " Apollo " + str(P2) + "\n")
            Bjab()
            sleep(randint(1,3))
       
    elif ran >= 5 and ran <= 6:
        if chance < 20:
            st.text(rocky + y)
            P1 = P1 + 3
            st.text("\nRocky Scores " + str(P1) + " Apollo " + str(P2) + "\n") 
            hook()
            sleep(randint(1,3))
       
        else:
            st.text(apollo + dy)
            st.text("\nRocky Scores " + str(P1) + " Apollo " + str(P2) + "\n") 
            Bhook()
            sleep(randint(1,3))
           
    elif ran >= 7 and ran <= 10:
        if chance <=33:
            st.text(apollo + x)
            P2 = P2 + 1
            st.text("\nRocky Scores " + str(P1) + " Apollo " + str(P2) + "\n")
            jab()
            sleep(randint(1,3))
           
        else:
            st.text(rocky + dx)
            st.text("\nRocky Scores " + str(P1) + " Apollo " + str(P2) + "\n")
            Bjab()
            sleep(randint(1,3))
       
    elif ran >= 11 and ran <= 12:
        if chance < 20:
            st.text(apollo + y)
            P2 = P2 + 3
            st.text("\nRocky Scores " + str(P1) + " Apollo " + str(P2) + "\n")
            hook()
            sleep(randint(1,3))
           
        else:
            st.text(rocky + dy)
            st.text("\nRocky Scores " + str(P1) + " Apollo " + str(P2) + "\n")
            Bhook()
            sleep(randint(1,3)) 
       
        #print("Player 2 Score " + str(P2)) 
           
    
