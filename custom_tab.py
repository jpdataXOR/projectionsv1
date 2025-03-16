import streamlit as st
from data_utils import get_stock_data, generate_future_projections_pattern, prepare_table
from chart_utils import plot_stock_chart
from datetime import datetime
import pandas as pd

def render_custom_tab():
    """
    Renders the Custom Stock Search tab UI and runs the analysis.
    """
    selected_symbol = None
    stock_label = None

    # Input UI for custom stock ticker
    custom_stock = st.text_input("Enter stock ticker symbol (e.g., AAPL, MSFT, GOOGL)")
    if custom_stock:
        selected_symbol = custom_stock
        stock_label = custom_stock

    # Analysis button for custom tab
    if st.button("Analyze (Custom)"):
        if not selected_symbol:
            st.error("Please enter a stock ticker symbol.")
        else:
            st.info(f"Analyzing: {stock_label}")
            # Intervals ordered as: weekly, daily, hourly.
            intervals = ["1wk", "1d", "1h"]
            for interval in intervals:
                st.subheader(f"Interval: {interval}")
                # Choose correct date format based on interval
                date_format = '%d-%b-%Y %H:%M' if interval == "1h" else '%d-%b-%Y'
                
                # Get stock data and projections for this interval
                stock_data = get_stock_data(selected_symbol, interval)
                future_projections = generate_future_projections_pattern(selected_symbol, interval)
                
                # Display current time and latest data timestamp for this interval
                current_time = datetime.now().strftime(date_format)
                latest_time = stock_data[-1]['date']
                st.write(f"Current Time: {current_time} | Latest Data Time: {latest_time}")
                
                # Plot and display the chart
                fig = plot_stock_chart(stock_data, future_projections, date_format)
                st.plotly_chart(fig)
                
                # Display the styled percentage change table (for the last 10 data points)
                styled_table = prepare_table(stock_data)
                st.dataframe(styled_table)
