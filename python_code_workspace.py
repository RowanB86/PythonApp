import pandas as pd
import plotly.express as px
import streamlit as st

# Load dataset
df = px.data.iris()

# Ensure correct data types
df["sepal_width"] = pd.to_numeric(df["sepal_width"], errors="coerce")
df["sepal_length"] = pd.to_numeric(df["sepal_length"], errors="coerce")

# Debugging: Check dataset
st.write("Dataset Info:")
st.write(df.info())
st.write(df.head())

# Check if the dataframe is empty
if df.empty:
    st.error("Dataset is empty. Check if it loaded correctly.")
else:
    # Create scatter plot
    fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species",
                     title="Iris Sepal Dimensions",
                     labels={"sepal_width": "Sepal Width (cm)", "sepal_length": "Sepal Length (cm)"})
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)
