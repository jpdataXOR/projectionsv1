import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from stock_options import stock_options  # Import stock options

# Function to fetch stock data
def get_stock_data(stock_symbol, interval):
    period = "1y" if interval == "1h" else "5y" if interval == "1d" else "max"
    
    instrument = yf.Ticker(stock_symbol)
    array_data = instrument.history(period=period, interval=interval, auto_adjust=False)

    date_format = '%d-%b-%Y %H:%M' if interval == "1h" else '%d-%b-%Y'
    
    stock_data = []
    
    for i in range(1, len(array_data)):  # Start from 1 to calculate % change
        close_price = array_data.iloc[i]['Close']
        prev_price = array_data.iloc[i - 1]['Close']
        percentage_change = ((close_price - prev_price) / prev_price) * 100

        stock_data.append({
            'date': array_data.index[i].strftime(date_format),
            'percentage_change': round(percentage_change, 2)  # Round for better readability
        })

    return stock_data

# Function to apply color styling
def highlight_cells(val):
    color = 'green' if val > 0 else 'red'
    intensity = min(abs(val) / 5, 1)  # Normalize to keep shades balanced
    return f'background-color: rgba({255 if val < 0 else 0}, {255 if val > 0 else 0}, 0, {intensity})'

# Streamlit UI
st.title("Stock Analysis App")

selected_stock = st.selectbox("Select a stock or index", list(stock_options.keys()))
selected_symbol = stock_options[selected_stock]
selected_interval = st.selectbox("Select an interval", ["1d", "1h", "1wk"])

if st.button("Analyze"):
    try:
        stock_data = get_stock_data(selected_symbol, selected_interval)

        # Convert data for plotting
        dates = [datetime.strptime(data['date'], '%d-%b-%Y') for data in stock_data]
        percentage_changes = [data['percentage_change'] for data in stock_data]

        # **Only keep the last 10 points for the chart**
        last_10_dates = dates[-10:]
        last_10_changes = percentage_changes[-10:]

        # Step Line Chart (Last 10 periods)
        step_trace = go.Scatter(
            x=last_10_dates,
            y=last_10_changes,
            mode='lines',
            line_shape='hv',  # Step-like movements
            name='Close % Change',
            marker=dict(color='blue')
        )

        fig = go.Figure(data=[step_trace])
        fig.update_layout(
            title="Stock % Change (Last 10 Periods)",
            xaxis_title="Date",
            yaxis_title="Close % Change",
            showlegend=False
        )
        st.plotly_chart(fig)

        # Display Data Table (Horizontal)
        stock_df = pd.DataFrame(stock_data[-10:])  # Only show last 10 points
        stock_df = stock_df.set_index("date").T  # Transpose to horizontal format

        # Apply color styling
        styled_df = stock_df.style.applymap(highlight_cells)

        st.dataframe(styled_df)  # Display styled dataframe

    except Exception as e:
        st.error(f"Error fetching stock data: {e}")
        st.info("This could be due to an invalid ticker symbol or no data available for the selected interval.")

if __name__ == "__main__":
    st.write("Ready to analyze stocks!")
