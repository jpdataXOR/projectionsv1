# app.py
import streamlit as st
from stock_options import stock_options
from data_utils import get_stock_data, generate_future_projections_pattern, prepare_table
from chart_utils import plot_stock_chart
import pandas as pd

st.title("Stock Analysis App")

selected_stock = st.selectbox("Select a stock or index", list(stock_options.keys()))
selected_symbol = stock_options[selected_stock]
selected_interval = st.selectbox("Select an interval", ["1d", "1h", "1wk"])

# Determine the correct date format based on the interval
date_format = '%d-%b-%Y %H:%M' if selected_interval == "1h" else '%d-%b-%Y'

if st.button("Analyze"):
    try:
        # Get actual stock data (list of dicts)
        stock_data = get_stock_data(selected_symbol, selected_interval)
        
        # Generate future projections using historical pattern matching logic
        future_projections = generate_future_projections_pattern(selected_symbol, selected_interval)
        
        # Plot chart: actual prices and future projection lines with labels
        fig = plot_stock_chart(stock_data, future_projections, date_format)
        st.plotly_chart(fig)
        
        # Display styled table of percentage changes for last 10 data points
        styled_table = prepare_table(stock_data)
        st.dataframe(styled_table)
        
    except Exception as e:
        st.error(f"Error fetching stock data: {e}")
        st.info("This could be due to an invalid ticker symbol or no data available for the selected interval.")

if __name__ == "__main__":
    st.write("Ready to analyze stocks!")
