import streamlit as st
import pandas as pd
import plotly.express as px

# Load dataset
df = px.data.iris()

# Debugging: Ensure column names and sample data are correct
st.write("Dataset Preview:")
st.write(df.head())

# Ensure correct data types
df["sepal_width"] = pd.to_numeric(df["sepal_width"], errors="coerce")
df["sepal_length"] = pd.to_numeric(df["sepal_length"], errors="coerce")

# Create scatter plot
fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species",
                 title="Iris Sepal Dimensions",
                 labels={"sepal_width": "Sepal Width (cm)", "sepal_length": "Sepal Length (cm)"})

# Debug: Check if the figure object exists
st.write("Figure Object:", fig)

# Display the chart
st.plotly_chart(fig, use_container_width=True)
