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


st.title('Data Science')
st.header('Data Collection')
st.subheader('Web Scraping')

if 'tables_dict' not in st.session_state:
    st.session_state.tables_dict = {}

if 'TableCount' not in st.session_state:
    st.session_state.TableCount = 0
    
URL = st.text_input("Enter URL:")
TableNum = st.text_input("Enter Table Number:")

AddTable = st.button("Add Table",key="AddTab")

def remove_outliers(df, column_name):
    Q1 = df[column_name].quantile(0.25)
    Q3 = df[column_name].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    filtered_df = df[(df[column_name] >= lower_bound) & (df[column_name] <= upper_bound)]
    return filtered_df

def plot_decision_boundary(model, X, y):
    # Create a mesh grid for our plot
    h = .02  # mesh step size
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

    # Use the model to make predictions on the mesh points
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    # Create the figure and plot the decision boundary
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.contourf(xx, yy, Z, alpha=0.8)

    # Plot the training points
    scatter = ax.scatter(X[:, 0], X[:, 1], c=y, s=40, edgecolor='k', cmap=plt.cm.jet)
    ax.set_xlabel("Principal Component 1")
    ax.set_ylabel("Principal Component 2")
    ax.set_title("Decision boundary of SVM")
    legend1 = ax.legend(*scatter.legend_elements(), loc="upper left", title="Classes")
    ax.add_artist(legend1)
    ax.set_xlim(X[:, 0].min() - 0.5, X[:, 0].max() + 0.5)
    ax.set_ylim(X[:, 1].min() - 0.5, X[:, 1].max() + 0.5)
    ax.set_xticks(())
    ax.set_yticks(())
    
    return fig


if AddTable:
    response = requests.get(URL)
    soup = BeautifulSoup(response.content,'html.parser')
    tables = soup.find_all('table',{"class": "wikitable", "class": "sortable"})
    st.session_state.TableCount += 1
    
    df = pd.read_html(str(tables[int(TableNum)-1]))[0]
    df.columns = [' '.join(col).strip() for col in df.columns.values]
    st.session_state.tables_dict[st.session_state.TableCount] = df

TableNumber = 1
for table_id,table_data in list(st.session_state.tables_dict.items()):
    st.write(table_data)
    
    delete_button = st.button(f"Delete Table {table_id}")
    if delete_button:
        st.session_state.TableCount -= 1
        del st.session_state.tables_dict[table_id]
        st.experimental_rerun()
    
    TableNumber += 1
    
if st.session_state.TableCount > 0:
    st.header('Data Cleansing')
    CleanTabNum = st.text_input("Enter Number of table to be cleansed:")
    try:
        selected_column = st.selectbox('Select column to clean:', st.session_state.tables_dict[int(CleanTabNum)].columns)    
    except:
       pass 
   
    clean_button = st.button("Clean Column")
    droprows_button = st.button("Drop rows with missing values")
    dropstringrows_button = st.button("Drop rows with non numeric values")
    impute_button = st.button("Impute missing values with mean")
    convert_to_numeric_button = st.button("Convert values to numeric")
    demo2_button = st.button("Demo button 2: Rename Columns")
    demo3_button = st.button("Demo button 3: Clean columns, convert to numeric and drop missing vals")
    
    if clean_button:
        df = st.session_state.tables_dict[int(CleanTabNum)]
        df[selected_column] = df[selected_column].str.split('[').str[0].str.strip()
        df[selected_column] = df[selected_column].str.split('*').str[0].str.strip()
        df[selected_column] = df[selected_column].str.rstrip()
        st.session_state.tables_dict[int(CleanTabNum)] = df
        st.experimental_rerun()
    
    if droprows_button:
        df = st.session_state.tables_dict[int(CleanTabNum)]
        df = df.dropna(subset=[selected_column])
        st.session_state.tables_dict[int(CleanTabNum)] = df
        st.experimental_rerun()   

    if dropstringrows_button:
        df = st.session_state.tables_dict[int(CleanTabNum)]
        df[pd.to_numeric(df[selected_column], errors='coerce').notna()]
        st.session_state.tables_dict[int(CleanTabNum)] = df
        st.experimental_rerun()  
    
    if convert_to_numeric_button:
        df = st.session_state.tables_dict[int(CleanTabNum)]
        df[selected_column] = pd.to_numeric(df[selected_column], errors='coerce')
        st.session_state.tables_dict[int(CleanTabNum)] = df
        st.experimental_rerun()      

    if impute_button:
        
        df = st.session_state.tables_dict[int(CleanTabNum)]
        df.replace([None], np.nan, inplace=True)
        df.fillna(st.session_state.tables_dict[int(CleanTabNum)].mean(), inplace=True)
        st.experimental_rerun()   
        
    if demo2_button:
        
        df = st.session_state.merged_df
        column_indices_to_rename = {6: "GDP",8: "Adult (25+) Literacy Rate", 9: "Life Expectancy",
                                    11: "Forest Area", 12: "Internet Users", 13: "Population Growth 15-20"}
        df.rename(columns={df.columns[index]: new_name for index, new_name in column_indices_to_rename.items()}, inplace=True)
        st.session_state.merged_df = df
        st.session_state.tables_dict[st.session_state.TableCount] = df
        st.experimental_rerun()  
    
    if demo3_button:
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
        st.experimental_rerun()   
        #if any(df.isnull()):
            #st.write("There are None values in this column!")
        #else:
            #st.write("There are no longer None values in this column!")

        #dtype_of_column = df[selected_column].dtype
        #st.write(f"Dtype of the column: {dtype_of_column}")
        #none_count = df[selected_column].isnull().sum() 
        #nan_count = df[selected_column].isna().sum()
        #st.write(f"Number of None values in column {selected_column} after replacement: {none_count}")
        #st.write(f"Number of NaN values in column {selected_column} after replacement: {nan_count}")

    NewName = st.text_input("Enter new column name:")
    rename_button = st.button("Rename column")

    if rename_button:
        df = st.session_state.tables_dict[int(CleanTabNum)]
        df.rename(columns={selected_column: NewName}, inplace=True)
        st.session_state.tables_dict[int(CleanTabNum)] = df
        st.experimental_rerun()  

    st.header('Data Manipulation')
    LTabNum = st.text_input("Enter Left Table Number:")
    RTabNum = st.text_input("Enter Right Table Number:")  
    try:
        selected_column1 = st.selectbox('Select left table join column:', st.session_state.tables_dict[int(LTabNum)].columns)
        
    except:
      pass

    try:
        selected_column2 = st.selectbox('Select right table join column:', st.session_state.tables_dict[int(RTabNum)].columns)
        
    except:
      pass      

    try:
        selected_column3 = st.selectbox('Select right table column to append to left table:', st.session_state.tables_dict[int(RTabNum)].columns)
    except:
      pass             
    
    merge_button = st.button("Perform Inner Join")
    demo1_button = st.button("Demo Button1: Merges tables")
    
    if merge_button:
        Lindex = st.session_state.tables_dict[int(LTabNum)].columns.get_loc(selected_column1)
        Rindex = st.session_state.tables_dict[int(RTabNum)].columns.get_loc(selected_column2)
        df1 = st.session_state.tables_dict[int(LTabNum)]
        df2 = st.session_state.tables_dict[int(RTabNum)]
        df2 = df2[[selected_column2, selected_column3]]
        merged_df = pd.merge(df1.set_index(df1.columns[Lindex]),df2.set_index(df2.columns[Rindex]),left_index=True,right_index=True).reset_index()
        merged_df = merged_df.rename(columns={"index": df1.columns[Lindex]})
        st.session_state.TableCount += 1
        st.session_state.tables_dict[st.session_state.TableCount] = merged_df
        st.write(merged_df)
        st.session_state.merged_df = merged_df
    
    if demo1_button:
        Lindex = 0
        Rindex = 0
        LTabNum = 8
        RTabNum = 3
        
        merged_df =  st.session_state.merged_df

        df1 = merged_df
        df2 = st.session_state.tables_dict[int(RTabNum)]
        df2 = df2.iloc[:, [0, 1]]
        merged_df = pd.merge(df1.set_index(df1.columns[Lindex]),df2.set_index(df2.columns[Rindex]),left_index=True,right_index=True).reset_index()
        merged_df = merged_df.rename(columns={"index": df1.columns[Lindex]})       

        LTabNum = 8
        RTabNum = 4
        
        df1 = merged_df
        df2 = st.session_state.tables_dict[int(RTabNum)]
        df2 = df2.iloc[:, [0, 4]]
        merged_df = pd.merge(df1.set_index(df1.columns[Lindex]),df2.set_index(df2.columns[Rindex]),left_index=True,right_index=True).reset_index()
        merged_df = merged_df.rename(columns={"index": df1.columns[Lindex]}) 


        LTabNum = 8
        RTabNum = 5
        
        df1 = merged_df
        df2 = st.session_state.tables_dict[int(RTabNum)]
        df2 = df2.iloc[:, [0, 4]]
        merged_df = pd.merge(df1.set_index(df1.columns[Lindex]),df2.set_index(df2.columns[Rindex]),left_index=True,right_index=True).reset_index()
        merged_df = merged_df.rename(columns={"index": df1.columns[Lindex]}) 


        LTabNum = 8
        RTabNum = 6

        df1 = merged_df
        df2 = st.session_state.tables_dict[int(RTabNum)]
        df2 = df2.iloc[:, [0, 3]]
        merged_df = pd.merge(df1.set_index(df1.columns[Lindex]),df2.set_index(df2.columns[Rindex]),left_index=True,right_index=True).reset_index()
        merged_df = merged_df.rename(columns={"index": df1.columns[Lindex]}) 


        LTabNum = 8
        RTabNum = 7
        
        df1 = merged_df
        df2 = st.session_state.tables_dict[int(RTabNum)]
        df2 = df2.iloc[:, [0, 6]]
        merged_df = pd.merge(df1.set_index(df1.columns[Lindex]),df2.set_index(df2.columns[Rindex]),left_index=True,right_index=True).reset_index()
        merged_df = merged_df.rename(columns={"index": df1.columns[Lindex]}) 

        st.session_state.TableCount += 1
        st.session_state.tables_dict[st.session_state.TableCount] = merged_df
        st.write(merged_df)
        st.session_state.merged_df = merged_df
        st.experimental_rerun() 

    if 'merged_df' in st.session_state:
        st.session_state.merged_df = st.session_state.tables_dict[st.session_state.TableCount]
        st.header("Exploratory Data Analysis")
        
        options = ['Scatter Plot', 'Box-Plot', 'Probability Density Plot']
        
        # Creating the select box
        selected_option = st.selectbox('Choose graph type:', options)       
        
        if selected_option == "Scatter Plot":
            options = list(st.session_state.merged_df.columns)
            var1 = st.selectbox('Select y-axis variable:',options)
            var2 = st.selectbox('Select x-axis variable:',options)
            
            if st.button("Plot Graph"):
                filtered_df = remove_outliers(st.session_state.merged_df, var1)
                filtered_df = remove_outliers(filtered_df, var2)

                fig = px.scatter(filtered_df, x=var2, y=var1, color=filtered_df.iloc[:,1], title='Scatterplot stratified by Continent')
                st.plotly_chart(fig)

        if selected_option == "Probability Density Plot":
            options = list(st.session_state.merged_df.columns)
            var1 = st.selectbox('Select y-axis variable:',options)
            variable_name = var1
            data = st.session_state.merged_df[variable_name]
            
            if st.button("Plot Graph"):
                # Plotting
                plt.figure(figsize=(10, 6))
                sns.kdeplot(data, shade=True)
                plt.title(f"Kernel Density Plot for {variable_name}")
                plt.xlabel(variable_name)
                plt.ylabel("Density")
                st.pyplot(plt) 
                
        if selected_option == "Box-Plot":
            options = list(st.session_state.merged_df.columns)
            var1 = st.selectbox('Select variable:',options)
            variable_name = var1
            data = st.session_state.merged_df[variable_name]
            
            if st.button("Plot Graph"):
                # Plotting
                filtered_df = remove_outliers(st.session_state.merged_df, var1)

                y_variable = var1
                
                data = filtered_df
                
                # Plotting
                plt.figure(figsize=(12, 8))
                sns.boxplot(x=data.iloc[:,1], y=data[y_variable])
                plt.title(f"Boxplot of {y_variable} by Continent")
                plt.xlabel("Continent")
                plt.ylabel(y_variable)
                st.pyplot(plt)
        
        st.subheader("Principal Component Analysis")
        features_to_include = st.multiselect(
         'Select features to include in PCA',
        options = list(st.session_state.merged_df.columns),
        )
        stratify_column = st.selectbox('Select column to stratify data points by:', st.session_state.merged_df.columns)
        
        PCA_Button = st.button("Perform PCA")
        
        # Here's the part where we map colors to continents
 

        if PCA_Button:
    
            # Extracting the selected numerical features
            x = st.session_state.merged_df[features_to_include].values
        
            # Standardizing the features
            x = StandardScaler().fit_transform(x)
        
            # Applying PCA
            pca = PCA(n_components=2)  # Using 2 components for visualization
            principalComponents = pca.fit_transform(x)
        
            # Converting to DataFrame for easier plotting
            principalDf = pd.DataFrame(data=principalComponents, columns=['Principal Component 1', 'Principal Component 2'])
    
            # Visualizing the results
            #fig, ax = plt.subplots(figsize=(10, 6))
            #ax.set_xlabel('Principal Component 1', fontsize=15)
            #ax.set_ylabel('Principal Component 2', fontsize=15)
            #ax.set_title('2-Component PCA', fontsize=20)
            #countries = st.session_state.merged_df.iloc[:, 0].values
            principalDf['Country'] = st.session_state.merged_df.iloc[:, 0].values
            principalDf['Continent'] = st.session_state.merged_df[stratify_column].values
            
            fig = px.scatter(principalDf, x='Principal Component 1', y='Principal Component 2', hover_data=['Country'])
        
            #for i, country in enumerate(countries):
                #ax.scatter(principalDf.loc[i, 'Principal Component 1'], principalDf.loc[i, 'Principal Component 2'], label=country)
        
            #ax.legend()
            #ax.grid(True)
            #st.pyplot(fig)
            unique_continents = st.session_state.merged_df[stratify_column].unique()
            colors = plt.cm.jet(np.linspace(0, 1, len(unique_continents)))
            color_map = dict(zip(unique_continents, colors))
            
            # Plotting
            fig, ax = plt.subplots(figsize=(10, 6))
            for continent, color in color_map.items():
                idx = principalDf['Continent'] == continent
                ax.scatter(principalDf.loc[idx, 'Principal Component 1'], principalDf.loc[idx, 'Principal Component 2'], c=[color], label=continent)
            
            ax.set_xlabel('Principal Component 1', fontsize=15)
            ax.set_ylabel('Principal Component 2', fontsize=15)
            ax.set_title('2-Component PCA with Color by Continent', fontsize=20)
            ax.legend()
            ax.grid(True)
            
            # Display the figure in Streamlit
            #st.pyplot(fig)
            

            st.session_state.principalDf = pd.DataFrame(data=principalComponents, columns=['Principal Component 1', 'Principal Component 2'])

            fig = px.scatter(principalDf, x='Principal Component 1', y='Principal Component 2',
                             color='Continent', hover_name='Country',
                             title="2-Component PCA with Continent Coloring",
                             color_discrete_sequence=px.colors.qualitative.Set1)  
            
            st.plotly_chart(fig)

            st.session_state.unique_continents = unique_continents
            st.session_state.color_map = color_map
            st.session_state.stratify_column= stratify_column
            
        
        if 'principalDf' in st.session_state:
            st.header("Statistical Modelling")
            st.subheader("Support Vector Machines (SVM)")
            SVM_button = st.button("Use SVM Model to Draw Decision Boundary to Classify Continents")
            
            stratify_column = st.session_state.stratify_column 
            
            if SVM_button:
                
                stratify_column = st.session_state.stratify_column 
                color_map = st.session_state.color_map
                principalDf = st.session_state.principalDf
                
                from sklearn.preprocessing import LabelEncoder
                label_encoder = LabelEncoder()
                encoded_labels = label_encoder.fit_transform(st.session_state.merged_df[stratify_column])
                st.session_state.merged_df["encoded_continent"] = encoded_labels
                # Splitting data into training and testing sets
                X_train, X_test, y_train, y_test = train_test_split(principalDf, st.session_state.merged_df["encoded_continent"], test_size=0.2, random_state=42)
                
                # Train SVM classifier
                svm_classifier = SVC(kernel='linear', C=1)
                svm_classifier.fit(X_train, y_train)
                fig = plot_decision_boundary(svm_classifier, np.array(principalDf), st.session_state.merged_df["encoded_continent"].values)
                st.pyplot(fig)  
                
                st.session_state.SVM_Run = True
                
            
            if 'SVM_Run' in st.session_state:
                
                stratify_column = st.session_state.stratify_column 
                st.subheader("Decision Tree Modelling")
                features_to_include = st.multiselect(
                 'Select features to include in Decision Tree Modelling',
                options = list(st.session_state.merged_df.columns),
                )
                
                stratify_column = st.session_state.stratify_column 
                label_encoder = LabelEncoder()
                encoded_labels = label_encoder.fit_transform(st.session_state.merged_df[stratify_column])
                st.session_state.merged_df["encoded_continent"] = encoded_labels

                DT_Button = st.button("Perform Decision Tree Modelling")            
                
                if DT_Button:
                    X = st.session_state.merged_df[features_to_include].values
                    
                    # Encode the target variable with LabelEncoder
                    label_encoder = LabelEncoder()
                    y_encoded = label_encoder.fit_transform(st.session_state.merged_df.iloc[:,1].values)
                    

                    # Training the Decision Tree
                    clf = DecisionTreeClassifier(max_depth=3)  # setting max_depth to 3 for visualization purposes
                    clf.fit(X, y_encoded)
                    
                    # Use the inverse_transform method on the label encoder to get class names in the correct order
                    class_names_ordered = label_encoder.inverse_transform(list(range(len(label_encoder.classes_))))
                    
                    fig, ax = plt.subplots(figsize=(20, 10))
                    plot_tree(clf, filled=True, feature_names=features_to_include, class_names=class_names_ordered, rounded=True, ax=ax)
                    st.pyplot(fig)