import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from data_utils import generate_future_projections_pattern
from etf_config import ETF_CONFIG

def fetch_and_normalize(stock, period="1y", interval="1d"):
    """
    Fetch historical data for a given stock and normalize its Close prices so that the first value is 1.
    Returns a DataFrame and the initial price.
    If no data is found, returns (None, None).
    """
    ticker = yf.Ticker(stock)
    df = ticker.history(period=period, interval=interval, auto_adjust=True)
    df = df.sort_index()
    if df.empty or "Close" not in df.columns:
        return None, None
    initial = df["Close"].iloc[0]
    df["Normalized"] = df["Close"] / initial
    df = df.reset_index()
    return df, initial

def plot_3d_predictions(stocks, period="1y", interval="1d", actual_points=10, pred_points=5, num_pred_lines=5):
    """
    For each stock in 'stocks', plot a 3D chart with:
      - Actual data: last 'actual_points' periods (solid line)
      - Predicted data: next 'pred_points' periods from each available prediction pattern (dotted lines)
    Axes:
      - x-axis: Time index (0, 1, 2, …)
      - y-axis: A small offset for visual separation (unique for each stock)
      - z-axis: Normalized price (each series starts at 1)
    """
    # Expecting stocks to be a list of dictionaries with keys "id" and "label".
    if not isinstance(stocks, list):
        st.error("Invalid stock list. Expected a list of dictionaries with 'id' and 'label'.")
        return None

    # Create an offset for each stock.
    offsets = {stock["id"]: idx * 0.1 for idx, stock in enumerate(stocks)}
    # Pre-define some colors for common stocks.
    default_colors = {"GOOG": "blue", "AAPL": "red", "NFLX": "green", "MSFT": "orange", "AMZN": "purple"}
    
    fig = go.Figure()

    for stock_data in stocks:
        stock = stock_data["id"]
        label = stock_data["label"]
        df, initial = fetch_and_normalize(stock, period, interval)
        if df is None:
            st.warning(f"No data found for {stock} ({label}). Skipping.")
            continue

        n = len(df)
        if n < actual_points:
            st.warning(f"Not enough data for {stock} ({label}). Skipping.")
            continue

        # Actual data: last 'actual_points' periods.
        df_actual = df.iloc[-actual_points:]
        x_actual = np.arange(actual_points)
        y_offset = offsets.get(stock, 0)
        y_actual = np.full(actual_points, y_offset)
        z_actual = df_actual["Normalized"].values

        # Plot actual data as a solid line.
        fig.add_trace(go.Scatter3d(
            x=x_actual,
            y=y_actual,
            z=z_actual,
            mode="lines",
            line=dict(color=default_colors.get(stock, "gray"), width=4),
            name=f"{label} Actual"
        ))

        # Add a label at the last actual point.
        fig.add_trace(go.Scatter3d(
            x=[x_actual[-1]],
            y=[y_actual[-1]],
            z=[z_actual[-1]],
            mode="text",
            text=[label],
            textposition="top center",
            showlegend=False
        ))

        # Generate predictions.
        pred = generate_future_projections_pattern(stock, interval, future_points=pred_points, num_lines=num_pred_lines)
        for pred_line in pred:
            pred_data = pred_line["data"]
            z_pred = np.array([item["close"] for item in pred_data]) / initial
            L = len(z_pred)
            x_pred = np.arange(actual_points - 1, actual_points - 1 + L)
            y_pred = np.full(L, y_offset)

            fig.add_trace(go.Scatter3d(
                x=x_pred,
                y=y_pred,
                z=z_pred,
                mode="lines",
                line=dict(color=default_colors.get(stock, "gray"), width=4, dash="dot"),
                showlegend=False
            ))

            # Add a label at the first prediction point.
            fig.add_trace(go.Scatter3d(
                x=[x_pred[0]],
                y=[y_pred[0]],
                z=[z_pred[0]],
                mode="text",
                text=[label],
                textposition="top center",
                showlegend=False
            ))

    fig.update_layout(
        width=1000,
        height=700,
        title="3D Predictions Comparison (Normalized)",
        scene=dict(
            xaxis_title="Time Index",
            yaxis_title="Offset",
            zaxis_title="Normalized Price"
        ),
        scene_camera=dict(
            eye=dict(x=-1.5, y=-2.5, z=0.8)
        ),
        margin=dict(l=0, r=0, t=50, b=0)
    )
    return fig

def render_3d_predictions_tab():
    st.header("3D Predictions Comparison")
    st.write("Below is the 3D prediction chart for the 1-day interval. For each stock, the last 10 periods of actual data (solid line) are shown, and predictions for the next 5 periods (dotted lines) are overlaid. Stocks are normalized so they all start at 1 and are separated by a small offset.")
    
    # Example: Standard stocks defined with id and label.
    stocks = [
        {"id": "GOOG", "label": "Alphabet"},
        {"id": "AAPL", "label": "Apple"},
        {"id": "NFLX", "label": "Netflix"},
        {"id": "MSFT", "label": "Microsoft"},
        {"id": "AMZN", "label": "Amazon"}
    ]
    
    st.subheader("Interval: 1d")
    fig = plot_3d_predictions(stocks, period="1y", interval="1d", actual_points=10, pred_points=5, num_pred_lines=5)
    st.plotly_chart(fig)

if __name__ == "__main__":
    render_3d_predictions_tab()
