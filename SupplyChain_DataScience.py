# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import streamlit as st
import pandas as pd
import numpy as np
import random
import folium
from streamlit_folium import folium_static

def perform_cog_analysis():
    data = st.session_state['edited_df']
    
    customerDF = data[data['Location Type'] == 'Customer']
    customers = customerDF["Location ID"].tolist()

    warehousesDF = data[data['Location Type'] == 'Warehouse']
    warehouses = warehousesDF["Location ID"].tolist()
    
    dist = {(i, j): (69*((warehousesDF["Longitude"][i+len(customers)]-customerDF["Longitude"][j])**2 + 
                         (warehousesDF["Latitude"][i+len(customers)]-customerDF["Latitude"][j])**2)**0.5) 
            for i in range(len(warehouses)) for j in range(len(customers))}
    
    d = {j: customerDF["Demand"][j] for j in range(len(customers))}
    
    P = st.session_state.get('P', 0)
    
    result = dist.items()
    listdata = list(result)
    
    flat_listdata = [(k[0], k[1], v) for k, v in listdata]
    
    try:
        distarray = np.array(flat_listdata)
    except ValueError as e:
        st.write("Error converting flat_listdata to numpy array:", e)
        distarray = None

    if distarray is not None:
        combinations = [[]]
        
        for element in warehouses:
            for sub_set in combinations.copy():
                new_sub_set = sub_set + [int(element)]
                combinations.append(new_sub_set)
        
        combinations2 = [element for element in combinations if len(element) == P]
        
        numCust = len(customers)
        cost = []
        
        for i in range(0, len(combinations2)):  
            combCost = 0
            for j in range(0, len(customers)):
                wCost = [d[j] * dist[(combinations2[i][k] - numCust, j)] for k in range(0, P)]
                combCost += min(np.array(wCost))
            cost.append(combCost)
        
        if cost:
            optComb = combinations2[cost.index(min(cost))]
        else:
            optComb = []

        services = []
        for j in range(0, numCust):
            wCost = [d[j] * dist[(optComb[k] - numCust, j)] for k in range(0, P)]
            closestW = optComb[wCost.index(min(np.array(wCost)))]
            services.append((data['Latitude'][j], data['Longitude'][j], 
                             data['Latitude'][closestW], data['Longitude'][closestW]))
        
        color_options = {'customer': 'red',
                         'supply': 'yellow',
                         'flow': 'black',
                         'warehouse': 'blue',
                         'candidate': 'black',
                         'other': 'gray'}
        # Instantiate map
        map1 = folium.Map(location=data[['Latitude', 'Longitude']].mean(),
                          fit_bounds=[[data['Latitude'].min(),
                                       data['Longitude'].min()],
                                      [data['Latitude'].max(),
                                       data['Longitude'].max()]])
        
        # Add volume points
        location = 1
        for _, row in data.iterrows():
            if location <= len(customers):
                folium.CircleMarker(location=[row['Latitude'],
                                              row['Longitude']],
                                    radius=(row['Circle Size']**0.5),
                                    color=color_options.get(
                                        str(row['Location Type']).lower(), 'gray'),
                                    tooltip=str(row['Location ID'])).add_to(map1)
                
            elif (location-1) in optComb:
                folium.CircleMarker(location=[row['Latitude'],
                                              row['Longitude']],
                                    radius=(row['Circle Size']**0.5),
                                    color='black',
                                    tooltip=str(row['Location ID'])).add_to(map1)
                
            else:
                folium.CircleMarker(location=[row['Latitude'],
                                              row['Longitude']],
                                    radius=(row['Circle Size']**0.5),
                                    color=color_options.get(
                                        str(row['Location Type']).lower(), 'gray'),
                                    tooltip=str(row['Location ID'])).add_to(map1)   
            location = location + 1
            
        for i in range(len(services)):
            folium.PolyLine([[services[i][0], services[i][1]],
                             [services[i][2], services[i][3]]]).add_to(map1)
            
        map1.fit_bounds(data[['Latitude', 'Longitude']].values.tolist())
        st.session_state['map'] = map1

st.title('Centre of Gravity Modelling')

NumCustomers = st.text_input("Enter number of customers")
NumWarehouses = st.text_input("Enter number of warehouses")
Central_Latt = st.text_input("Enter Central Lattitude")
Central_Long = st.text_input("Enter Central Longitude")
Radius =  st.text_input("Enter Radius (miles) that all customers / warehouses will reside " +
                        " within.")

data = pd.DataFrame(columns=['Location ID','Latitude','Longitude','Circle Size','Location Type','Demand'])

if 'P' not in st.session_state:
    st.session_state.P = 0

SetLocations = st.button("Set warehouse / customer locations", key="SetLocations")

if SetLocations or 'TableCreated' in st.session_state:
    if SetLocations or 'TableCreated' not in st.session_state:
        minLong = float(Central_Long) - (float(Radius)/69)
        maxLong = float(Central_Long) + (float(Radius)/69)      
        
        minLatt = float(Central_Latt) - (float(Radius)/69)
        maxLatt = float(Central_Latt) + (float(Radius)/69)     
        
        for i in range(0, int(NumCustomers)):
            Latt = random.randint(int(minLatt*10000), int(maxLatt*10000)) / 10000
            Long = random.randint(int(minLong*10000), int(maxLong*10000)) / 10000
    
            newRow = {
                'Location ID': str(i),
                'Latitude': Latt,
                'Longitude': Long,
                'Circle Size': 70,
                'Location Type': 'Customer',
                'Demand': 50
            }    
    
            data = pd.concat([data, pd.DataFrame(newRow, index=[i])])
            
        for i in range(0, int(NumWarehouses)):
            Latt = random.randint(int(minLatt*10000), int(maxLatt*10000)) / 10000
            Long = random.randint(int(minLong*10000), int(maxLong*10000)) / 10000
    
            newRow = {
                'Location ID': str(i + int(NumCustomers)),
                'Latitude': Latt,
                'Longitude': Long,
                'Circle Size': 70,
                'Location Type': 'Warehouse',
                'Demand': 0
            }    
    
            data = pd.concat([data, pd.DataFrame(newRow, index=[i + int(NumCustomers)])], ignore_index=False)
        
        st.session_state.TableCreated = True
        st.session_state['edited_df'] = data
    
    edited_df = st.data_editor(st.session_state['edited_df'], key="data_editor", on_change=perform_cog_analysis)
    
    P = st.text_input("Enter Number of Warehouses to be selected by COG Model", value=st.session_state.P, key="P")
    st.session_state.P = P
    
    PerformCOG = st.button("Perform Centre of Gravity Analysis", key="COG")
    
    if PerformCOG:
        perform_cog_analysis()

if 'map' in st.session_state:
    st_data = folium_static(st.session_state['map'], width=725)
