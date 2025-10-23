import streamlit as st
import pandas as pd
import plotly.express as px
from interface import english_to_sql_gemini, run_query, get_bigquery_schema

# Page config
st.set_page_config(
    page_title="Talk to Your Database",
    page_icon="🤖",
    layout="wide"
)

# Title
st.title("🤖 Talk to Your Database")
st.markdown("Ask questions about your data in plain English")

# Get schema
try:
    schema_hint = get_bigquery_schema("talk2urdatbase")
except Exception as e:
    st.error(f"Could not load schema: {str(e)}")
    st.stop()

# User input
user_question = st.text_input("Enter your question:", placeholder="Example: Show me average annual salary by department")

if user_question:
    try:
        # Generate SQL
        sql_query = english_to_sql_gemini(user_question, schema_hint)
        
        # Show SQL
        with st.expander("View Generated SQL"):
            st.code(sql_query, language="sql")
        
        # Run query
        df = run_query(sql_query)
        
        # Show results in tabs
        tab1, tab2 = st.tabs(["Data", "Visualization"])
        
        with tab1:
            st.dataframe(df)
        
        with tab2:
            # Automatic visualization based on data
            if not df.empty:
                numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
                if len(numeric_cols) > 0:
                    # Let user select columns for visualization
                    y_col = st.selectbox("Select value to plot:", numeric_cols)
                    categorical_cols = df.select_dtypes(exclude=['float64', 'int64']).columns
                    if len(categorical_cols) > 0:
                        x_col = st.selectbox("Group by:", categorical_cols)
                        fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("No categorical columns available for grouping")
                else:
                    st.warning("No numeric columns available for visualization")
            else:
                st.warning("No data to visualize")
                
    except Exception as e:
        st.error(f"Error: {str(e)}")