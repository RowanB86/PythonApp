
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 16:49:52 2023

@author: RowanBarua
"""

import streamlit as st
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import plotly.express as px
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.preprocessing import LabelEncoder
import seaborn as sns
from sklearn.cluster import KMeans
import plotly.express as px
import plotly.graph_objs as go

st.title('Classification and Clustering')


if 'tables_dict' not in st.session_state:
    st.session_state.tables_dict = {}

if 'TableCount' not in st.session_state:
    st.session_state.TableCount = 0

st.markdown("""
<div style="
    border: 3px solid #0056b3; 
    border-radius: 10px;
    padding: 20px;
    margin-top: 20px;
    margin-bottom: 30px;  /* This is the bottom margin to create space after the div */
    background-color: #e1f5fe;
    color: #0d47a1;
">
    <h4 style="color: #1565c0;">Interactive Demonstration of Clustering</h4>
    <p>Clustering is used to identify data points that are similar based on their proximity to one another, allowing them to be classified into categories. A practical application of clustering is in customer profiling, where attributes like age and monthly spend are analyzed to segment customers for tailored services or offers.</p>
    <p>Please press the "Generate demo data table" button.</p>
</div>
""", unsafe_allow_html=True)

# Your button (this will now appear with space below the div)
demo4_button = st.button("Generate demo data table")
st.empty()
st.empty()
st.empty()
#st.markdown("""
##- <span style="color: red;">**Bullet Point 1:**</span> Description of the first point.
#- <span style="color: red;">**Bullet Point 2:**</span> Description of the second point.
#- <span style="color: red;">**Bullet Point 3:**</span> Description of the third point.
#""", unsafe_allow_html=True)

if demo4_button:
    
    
    
    start_table_number = max(st.session_state.TableCount,1) 
    
    URLs = ['https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)',
            'https://en.wikipedia.org/wiki/List_of_countries_by_literacy_rate',
            'https://en.wikipedia.org/wiki/List_of_countries_by_life_expectancy',
            'https://en.wikipedia.org/wiki/List_of_countries_by_carbon_dioxide_emissions',
            'https://en.wikipedia.org/wiki/List_of_countries_by_forest_area',
            'https://en.wikipedia.org/wiki/List_of_countries_by_number_of_Internet_users',
            'https://en.wikipedia.org/wiki/List_of_countries_by_population_growth_rate']
    
    for i in range(0,len(URLs)):
        if i == 4:
            wiki_table_number = 2
        else:
            wiki_table_number = 1
        
        response = requests.get(URLs[i])
        soup = BeautifulSoup(response.content,'html.parser')
        tables = soup.find_all('table',{"class": "wikitable", "class": "sortable"})
        st.session_state.TableCount += 1        
        df = pd.read_html(str(tables[int(wiki_table_number)-1]))[0]
        df.columns = [' '.join(col).strip() for col in df.columns.values]
        st.session_state.tables_dict[st.session_state.TableCount] = df
        st.session_state.merged_df = df
        
    for i in range(0,2):
        if i == 0:
            tab_num = start_table_number + 1
        else:
            tab_num = start_table_number + 6
        
            
        df = st.session_state.tables_dict[int(tab_num)]
        df.iloc[:,0] = df.iloc[:,0].str.split('[').str[0].str.strip()
        df.iloc[:,0] = df.iloc[:,0].str.split('*').str[0].str.strip()
        df.iloc[:,0] = df.iloc[:,0].str.rstrip()
        st.session_state.tables_dict[int(tab_num)] = df
        #st.experimental_rerun()     
    
    Lindex = 0
    Rindex = 0

    LTabNum = start_table_number 
    RTabNum = start_table_number + 1
    
    df1 = st.session_state.tables_dict[int(LTabNum)]
    df2 = st.session_state.tables_dict[int(RTabNum)]
    df2 = df2.iloc[:, [0, 3]]

    merged_df = pd.merge(df1.set_index(df1.columns[Lindex]),df2.set_index(df2.columns[Rindex]),left_index=True,right_index=True).reset_index()
    merged_df = merged_df.rename(columns={"index": df1.columns[Lindex]})          
    
    LTabNum = start_table_number
    RTabNum = start_table_number + 2
    

    df1 = merged_df
    df2 = st.session_state.tables_dict[int(RTabNum)]
    df2 = df2.iloc[:, [0, 1]]
    merged_df = pd.merge(df1.set_index(df1.columns[Lindex]),df2.set_index(df2.columns[Rindex]),left_index=True,right_index=True).reset_index()
    merged_df = merged_df.rename(columns={"index": df1.columns[Lindex]})       

    LTabNum = start_table_number
    RTabNum = start_table_number + 3
    
    df1 = merged_df
    df2 = st.session_state.tables_dict[int(RTabNum)]
    df2 = df2.iloc[:, [0, 4]]
    merged_df = pd.merge(df1.set_index(df1.columns[Lindex]),df2.set_index(df2.columns[Rindex]),left_index=True,right_index=True).reset_index()
    merged_df = merged_df.rename(columns={"index": df1.columns[Lindex]}) 


    LTabNum = start_table_number
    RTabNum = start_table_number + 4
    
    df1 = merged_df
    df2 = st.session_state.tables_dict[int(RTabNum)]
    df2 = df2.iloc[:, [0, 4]]
    merged_df = pd.merge(df1.set_index(df1.columns[Lindex]),df2.set_index(df2.columns[Rindex]),left_index=True,right_index=True).reset_index()
    merged_df = merged_df.rename(columns={"index": df1.columns[Lindex]}) 


    LTabNum = start_table_number
    RTabNum = start_table_number + 5

    df1 = merged_df
    df2 = st.session_state.tables_dict[int(RTabNum)]
    df2 = df2.iloc[:, [0, 3]]
    merged_df = pd.merge(df1.set_index(df1.columns[Lindex]),df2.set_index(df2.columns[Rindex]),left_index=True,right_index=True).reset_index()
    merged_df = merged_df.rename(columns={"index": df1.columns[Lindex]}) 


    LTabNum = start_table_number
    RTabNum = start_table_number + 6
    
    df1 = merged_df
    df2 = st.session_state.tables_dict[int(RTabNum)]
    df2 = df2.iloc[:, [0, 6]]
    merged_df = pd.merge(df1.set_index(df1.columns[Lindex]),df2.set_index(df2.columns[Rindex]),left_index=True,right_index=True).reset_index()
    merged_df = merged_df.rename(columns={"index": df1.columns[Lindex]}) 

    st.session_state.TableCount += 1
    st.session_state.tables_dict[st.session_state.TableCount] = merged_df
    st.session_state.merged_df = merged_df   

    df = st.session_state.merged_df
    column_indices_to_rename = {0: "Country/Territory", 1: "UN Region", 6: "GDP",8: "Adult (25+) Literacy Rate", 9: "Life Expectancy",
                                11: "Forest Area", 12: "Internet Users", 13: "Population Growth 2015-2020"}
    df.rename(columns={df.columns[index]: new_name for index, new_name in column_indices_to_rename.items()}, inplace=True)
    st.session_state.merged_df = df
    st.session_state.tables_dict[st.session_state.TableCount] = df
    st.session_state.merged_table_num = st.session_state.TableCount

    df = st.session_state.merged_df

    df.iloc[:,6] = df.iloc[:,6].str.split('[').str[0].str.strip()
    df.iloc[:,6] = df.iloc[:,6].str.split('*').str[0].str.strip()
    df.iloc[:,6] = df.iloc[:,6].str.rstrip()

    df.iloc[:,6] = pd.to_numeric(df.iloc[:,6], errors='coerce')
    col_name = df.columns[6]
    df = df.dropna(subset=[col_name])
    
    for j in range(8,14):
       try:
           df.iloc[:,j] = df.iloc[:,j].str.split('[').str[0].str.strip()
           df.iloc[:,j] = df.iloc[:,j].str.split('*').str[0].str.strip()
           df.iloc[:,j] = df.iloc[:,j].str.rstrip()
       except:
           pass
       df.iloc[:,j] = pd.to_numeric(df.iloc[:,j], errors='coerce')
       col_name = df.columns[j]
       df = df.dropna(subset=[col_name])
    
    st.session_state.merged_df = df
    st.session_state.tables_dict[st.session_state.TableCount] = df
    
    col_nums = [2,3,4,5,7]
    column_names = []
    
    for i in range(0,5):
        column_names.append(df.columns[col_nums[i]])
    
    df.drop(columns=column_names,inplace=True)
    
    st.experimental_rerun()           

def remove_outliers(df, column_name):
    Q1 = df[column_name].quantile(0.25)
    Q3 = df[column_name].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    filtered_df = df[(df[column_name] >= lower_bound) & (df[column_name] <= upper_bound)]
    return filtered_df

def plot_decision_boundary(model, data, centers, original_data, variable_1, variable_2, color_dict, unique_regions):
    # Create the mesh grid with a suitable step size to reduce data size
    h_x = 0.1  # step size for the x-axis
    h_y = 0.01
    

    x_min, x_max = data[:, 0].min() - 1, data[:, 0].max() + 1
    y_min, y_max = data[:, 1].min() - 1, data[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h_x), np.arange(y_min, y_max, h_y))

    # Predict cluster labels for each point in the mesh grid
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    
    # Reshape the predicted labels to match xx's shape
    Z = Z.reshape(xx.shape)

    # Define the figure
    fig = go.Figure()

    # Create a contour plot for the cluster boundaries
    contour = go.Contour(
        x=xx[0, :],
        y=yy[:, 0],
        z=Z,
        showscale=False,  # This will remove the color scale
        contours_coloring='lines',  # Use lines for contours
        line_width=2  # Set the width of the contour lines
    )

    # Add the contour plot first to ensure it's below the scatter plot
    fig.add_trace(contour)

    # Add the scatter plot for the actual data points with UN Regions
    fig.add_trace(go.Scattergl(
        x=original_data[variable_1],
        y=original_data[variable_2],
        mode='markers+text',
        text=original_data['Country/Territory'],  # Use the country names as labels
        marker=dict(
            color=original_data['UN Region'].map(color_dict),  # Use the mapped colors
            size=12,  # Increased size for visibility
            opacity=0.5,  # Set the opacity to make markers more transparent
            line=dict(width=2, color='DarkSlateGrey')  # Increased line width for visibility
        ),
        textposition='top center',
        hoverinfo='text',
        showlegend=False  # Do not include this scatter plot in the legend
    ))
    
    # Add cluster centers to the figure
    for i, center in enumerate(centers):
        fig.add_trace(go.Scattergl(
            x=[center[0]],
            y=[center[1]],
            mode='markers',
            marker=dict(
                color='black',
                size=10,
                symbol='x'
            ),
            name=f"Cluster Center {i}",
            showlegend=True
        ))

    # Print the color_dict for debugging
    print("Color Dictionary:", color_dict)

    # Update the layout to include the correct titles and legend info
    fig.update_layout(
        title='Clustering of Countries with Decision Boundary',
        xaxis_title=variable_1,
        yaxis_title=variable_2,
        autosize=False,
        height=1500,  # You can adjust the size
        width=1000,
        legend_title_text='Legend'
    )

    # Update the legend to include the UN Region names
    legend_entries = [go.Scatter(x=[None], y=[None], mode='markers', 
                                 marker=dict(color=color_dict[region], size=10), 
                                 name=region) for region in unique_regions]
    for entry in legend_entries:
        fig.add_trace(entry)

    return fig

if st.session_state.TableCount > 0:
    df = st.session_state.merged_df
    
    st.markdown("""
    <div style="
        border: 3px solid #0056b3; 
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
        margin-bottom: 30px;  /* This is the bottom margin to create space after the div */
        background-color: #e1f5fe;
        color: #0d47a1;
    ">
        <p>The dataset below details countries in terms of variables such as GDP, Adult Literacy Rate (ages 25+), Life Expectancy etc. 
        To illustrate the power of clustering techniques we will apply a clustering algorithm known as "K-means" to attempt to 
        categorise countries in a meaningful way.</p>
        
    </div>
    """, unsafe_allow_html=True)    

    table_id = st.session_state.merged_table_num
    table_data = st.session_state.tables_dict[table_id]
    st.write(table_data)

    st.markdown("""
    <div style="
        border: 3px solid #0056b3; 
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
        margin-bottom: 30px;  /* This is the bottom margin to create space after the div */
        background-color: #e1f5fe;
        color: #0d47a1;
    ">
        <p>For simplicity, we will experiment with the effectiveness of clustering countries based on just two variables. If the afforementioned term
        "data point" is confusing to anyone, consider that each row of this table corresponds to a data point that can be illustrated graphically.</p>
        <p>Please select two variables that you think will be particularly effective for discriminating between countries, enter the number of clusters you want to create (more than 5 might be too many)
        and then press the "Show Clusters" button. See if you effectively you can separate the countries by continent. Note that this would probably be more achievable in more dimensions.
        I intend to develop this training to allow more dimensions.</p>
        
    </div>
    """, unsafe_allow_html=True)    
    
    num_cols = len(df.columns)
    col_names = []
    
    for i in range(2,num_cols):
        col_names.append(df.columns[i])
    
    variable_1 = st.selectbox('Select the first variable:', col_names)
    variable_2 = st.selectbox('Select the second variable:', col_names)
    num_clusters = st.text_input("Enter Number of Clusters to Create (up to 5 is recommended):")
    
    #st.experimental_rerun()
    def remove_outliers(df, column_name):
        Q1 = df[column_name].quantile(0.25)
        Q3 = df[column_name].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
    
        filtered_df = df[(df[column_name] >= lower_bound) & (df[column_name] <= upper_bound)]
        return filtered_df
    # Function to apply k-means
    def apply_kmeans(data, selected_data, n_clusters):
          # Check the first few rows of the data
        try:
            
            data_filtered = data
            
            
            selected_data = pd.DataFrame(selected_data,columns=[variable_1, variable_2])
            selected_data_filtered = selected_data

            
            for i in range(0,len(selected_data.columns)):
                data_filtered = remove_outliers(data_filtered, selected_data.columns[i]) 
                selected_data_filtered = remove_outliers(selected_data_filtered, selected_data.columns[i])
            # Convert selected_data to a DataFrame
            selected_df_filtered = pd.DataFrame(selected_data_filtered)

            # Apply K-means clustering on filtered data
            model = KMeans(n_clusters=n_clusters)
            clusters = model.fit_predict(selected_data_filtered)
            clustered_data = data_filtered.copy()
            clustered_data['Cluster'] = clusters

    
            # Define custom color mapping based on UN Region
            color_dict = {
                'Africa': '#AB63FA',    # Purple
                'Asia': '#FFD700',      # Yellow
                'Europe': '#00CC96',    # Teal
                'Americas': '#EF553B',  # Red
                'Oceania': '#FFA15A'    # Orange
            }
            unique_regions = clustered_data['UN Region'].unique()
    
            return clustered_data, model.cluster_centers_, model, color_dict, unique_regions,selected_df_filtered
        except Exception as e:
            print("Error in KMeans clustering:", e)  # Catch and print any errors during clustering
            raise e
    #TableNumber += 1
    
    
    if st.button('Show Clusters'):
        num_clusters = int(num_clusters)
        # Select the data for clustering
        selected_data = df[[variable_1, variable_2]].copy()  # Create a copy for scaling
    
        # Initialize and apply a scaler
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(selected_data)  # Scale the data
    
        # Update the original df with the scaled data
        df[[variable_1, variable_2]] = scaled_data
    
        # Perform K-means clustering using the scaled data
        model = KMeans(n_clusters=3)  # Assuming you want 3 clusters
        clusters = model.fit_predict(scaled_data)  # Use scaled data for fitting
        df['Cluster'] = clusters  # Add the cluster labels to the original df

        # Store the scaler in session state for inverse transforming later if needed
        st.session_state.scaler = scaler
    
        # Assume you have a color_dict ready for the color mapping
        color_dict = {
            'Africa': '#AB63FA', 
            'Asia': '#FFD700', 
            'Europe': '#00CC96', 
            'Americas': '#EF553B', 
            'Oceania': '#FFA15A'
        }
        unique_regions = df['UN Region'].unique()
    
        # Apply the k-means function
        # The apply_kmeans function should be defined to accept the data and return the clustering output
        clustered_data, centers, model, color_dict, unique_regions, scaled_data_df = apply_kmeans(df, scaled_data,num_clusters)
    
        # Update session state with required information
        st.session_state.df = df  # The df with the scaled variables and clusters
        st.session_state.model = model
        st.session_state.centers = centers
        st.session_state.color_dict = color_dict
        st.session_state.unique_regions = unique_regions
        st.session_state.variable_1 = variable_1
        st.session_state.variable_2 = variable_2
        st.session_state.selected_data = np.array(scaled_data_df)
        st.session_state.clustered_data = clustered_data
        selected_data_np = st.session_state.selected_data
       
        try:
            fig = plot_decision_boundary(
                st.session_state.model,
                selected_data_np,
                st.session_state.centers,
                st.session_state.clustered_data,  # Pass the clustered data, which contains the scaled variables
                st.session_state.variable_1,
                st.session_state.variable_2,
                st.session_state.color_dict,
                st.session_state.unique_regions
            )
            st.plotly_chart(fig)
        except Exception as e:
            st.error(f"An error occurred: {e}")
            
