# app.py
import streamlit as st
from stock_options import stock_options            # Import the full stock options list
from data_utils import get_stock_data, generate_future_projections, prepare_table  # Data functions
from chart_utils import plot_stock_chart            # Chart function

st.title("Stock Analysis App")

# Select stock and interval
selected_stock = st.selectbox("Select a stock or index", list(stock_options.keys()))
selected_symbol = stock_options[selected_stock]
selected_interval = st.selectbox("Select an interval", ["1d", "1h", "1wk"])

if st.button("Analyze"):
    try:
        # Get actual stock data
        stock_data = get_stock_data(selected_symbol, selected_interval)
        
        # Generate future projection lines (5 lines, 10 future points each)
        future_projections = generate_future_projections(stock_data)
        
        # Plot the chart (actual prices + future projections)
        fig = plot_stock_chart(stock_data, future_projections)
        st.plotly_chart(fig)
        
        # Display a styled table for percentage changes with color coding
        styled_table = prepare_table(stock_data)
        st.dataframe(styled_table)
        
    except Exception as e:
        st.error(f"Error fetching stock data: {e}")
        st.info("This could be due to an invalid ticker symbol or no data available for the selected interval.")

if __name__ == "__main__":
    st.write("Ready to analyze stocks!")
