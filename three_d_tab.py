# three_d_tab.py
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

def fetch_and_normalize(stock, period="1y", interval="1d"):
    """Fetch historical data and normalize the Close prices so that the first value is 1."""
    ticker = yf.Ticker(stock)
    df = ticker.history(period=period, interval=interval, auto_adjust=True)
    df = df.sort_index()  # Ensure ascending order
    initial = df['Close'].iloc[0]
    df['Normalized'] = df['Close'] / initial
    df = df.reset_index()  # Make the date a column
    return df

def plot_3d_comparison(stocks, period="1y", interval="1d"):
    """
    Plots a 3D comparison of multiple stocks.
    - x-axis: Time index (a simple integer index for each data point)
    - y-axis: A small offset for visual separation (unique for each stock)
    - z-axis: Normalized price (each stock's close divided by its initial close)
    """
    # Fetch and normalize data for each stock
    data_frames = {}
    for stock in stocks:
        data_frames[stock] = fetch_and_normalize(stock, period, interval)
    
    # Use only the overlapping range of data
    min_len = min([len(df) for df in data_frames.values()])
    for stock in stocks:
        data_frames[stock] = data_frames[stock].iloc[:min_len]
    
    # Create a time index (e.g., 0, 1, 2, …, min_len-1)
    x = np.arange(min_len)
    
    # Define a small offset for each stock for visual separation
    offsets = {
        "GOOG": 0.0,
        "AAPL": 0.05,
        "NFLX": 0.10,
        "MSFT": 0.15,
        "AMZN": 0.20
    }
    
    # Predefined colors for each stock
    colors = {
        "GOOG": "blue",
        "AAPL": "red",
        "NFLX": "green",
        "MSFT": "orange",
        "AMZN": "purple"
    }
    
    fig = go.Figure()
    for stock in stocks:
        df = data_frames[stock]
        x_vals = x  # Time index
        y_vals = np.full(min_len, offsets.get(stock, 0))  # Constant offset for each stock
        z_vals = df['Normalized'].values  # Normalized price on z-axis
        
        fig.add_trace(go.Scatter3d(
            x=x_vals,
            y=y_vals,
            z=z_vals,
            mode='lines',  # Simple line (no markers)
            line=dict(color=colors.get(stock, 'gray'), width=4),
            name=stock
        ))
    
    fig.update_layout(
        title="3D Comparison of Stocks (Normalized)",
        scene=dict(
            xaxis_title="Time Index",
            yaxis_title="Offset",
            zaxis_title="Normalized Price"
        )
    )
    return fig

def render_3d_tab():
    st.header("3D Comparison of Multiple Stocks")
    st.write("This 3D chart compares GOOG, AAPL, NFLX, MSFT, and AMZN. The x-axis represents a simple time index, the y-axis is a small offset applied to each stock for visual separation, and the z-axis shows the normalized price (each series starts at 1).")
    stocks = ["GOOG", "AAPL", "NFLX", "MSFT", "AMZN"]
    fig = plot_3d_comparison(stocks, period="1y", interval="1d")
    st.plotly_chart(fig)

if __name__ == "__main__":
    render_3d_tab()
