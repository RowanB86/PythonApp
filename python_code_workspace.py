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
        exec(updated_code, {}, local_namespace)  # Execute code safely
        fig = local_namespace.get("fig")  # Extract Plotly figure

        if isinstance(fig, go.Figure):
            st.success("✅ Chart generated successfully!")
            st.plotly_chart(fig)  # Display chart
        else:
            st.warning("⚠ No valid Plotly figure ('fig') found in the code.")

    except Exception as e:
        st.error(f"❌ Error: {e}")

