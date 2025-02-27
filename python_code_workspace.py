import streamlit as st
from streamlit_ace import st_ace
import plotly.express as px
import plotly.graph_objects as go

# Default example code
default_code = """
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# Generate sample data
df = px.data.iris()

# Create scatter plot
fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species",
                 title="Iris Sepal Dimensions",
                 labels={"sepal_width": "Sepal Width (cm)", "sepal_length": "Sepal Length (cm)"})
"""

# Streamlit App Layout
st.title("📊 Python Code Workspace for Plotly Charts")

# Code Editor
st.subheader("📝 Write your Python code here:")
updated_code = st_ace(value=default_code, language="python", theme="monokai", key="code-editor", height=400)

# Run Button
if st.button("Run Code"):
    local_namespace = {}
    try:
        exec(updated_code, {}, local_namespace)  # Use a dedicated namespace
        if "fig" in local_namespace:  # Check in local_namespace instead of locals()
            st.success("✅ Chart generated successfully!")
            st.plotly_chart(local_namespace["fig"])
        else:
            st.error("⚠️ No figure object found. Ensure your script assigns a `fig` variable.")
    except Exception as e:
        st.error(f"❌ Error in code execution: {e}")

  if "df" in local_namespace:
      st.write("Dataset Preview:", local_namespace["df"].head())
