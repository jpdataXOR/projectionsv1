import streamlit as st
from stock_options import stock_options
from data_utils import get_stock_data, generate_future_projections_pattern, prepare_table
from chart_utils import plot_stock_chart
import pandas as pd

st.title("Stock Analysis App")

# Create tabs for Predefined Stocks and Custom Stock Search
tab1, tab2 = st.tabs(["Predefined Stocks", "Custom Stock Search"])

selected_symbol = None
selected_method = None
stock_label = None

with tab1:
    predefined_stock = st.selectbox("Select a stock or index", list(stock_options.keys()))
    if predefined_stock:
        selected_symbol = stock_options[predefined_stock]
        selected_method = "dropdown"
        stock_label = predefined_stock  # Use the stock name from the dropdown

with tab2:
    custom_stock = st.text_input("Enter stock ticker symbol (e.g., AAPL, MSFT, GOOGL)")
    if custom_stock:
        selected_symbol = custom_stock
        selected_method = "custom"
        stock_label = custom_stock  # Use the custom ticker as the label

if st.button("Analyze"):
    if not selected_symbol:
        st.error("Please select a stock or enter a custom ticker symbol")
    else:
        st.info(f"Analyzing: {stock_label}")
        intervals = ["1h", "1d", "1wk"]
        # Run analysis for each interval one after the other
        for interval in intervals:
            st.subheader(f"Interval: {interval}")
            # Set date format based on interval
            date_format = '%d-%b-%Y %H:%M' if interval == "1h" else '%d-%b-%Y'
            
            # Get stock data and projections for this interval
            stock_data = get_stock_data(selected_symbol, interval)
            future_projections = generate_future_projections_pattern(selected_symbol, interval)
            
            # Plot and display the chart
            fig = plot_stock_chart(stock_data, future_projections, date_format)
            st.plotly_chart(fig)
            
            # Display the styled percentage change table (for the last 10 data points)
            styled_table = prepare_table(stock_data)
            st.dataframe(styled_table)

if __name__ == "__main__":
    st.write("Ready to analyze stocks!")
