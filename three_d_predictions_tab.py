# three_d_predictions_tab.py
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from data_utils import generate_future_projections_pattern


def fetch_and_normalize(stock, period="1y", interval="1d"):
    """
    Fetch historical data and normalize the Close prices so that the first value is 1.
    Returns the DataFrame and the initial raw close price.
    """
    ticker = yf.Ticker(stock)
    df = ticker.history(period=period, interval=interval, auto_adjust=True)
    df = df.sort_index()  # Ensure ascending order
    initial = df['Close'].iloc[0]
    df['Normalized'] = df['Close'] / initial
    df = df.reset_index()  # Make the date a column
    return df, initial


def plot_3d_predictions(stocks, period="1y", interval="1d", actual_points=10, pred_points=5, num_pred_lines=5):
    """
    For each stock in 'stocks', plot a 3D chart with:
      - Actual data: last 'actual_points' periods (solid line)
      - Predicted data: next 'pred_points' periods from each available prediction (dotted lines)
    Axes:
      - x-axis: Time index (0, 1, 2, …)
      - y-axis: A small offset for visual separation (unique for each stock)
      - z-axis: Normalized price (each series starts at 1)
    """
    # Define a unique offset and color for each stock.
    offsets = {
        "GOOG": 0.0,
        "AAPL": 0.05,
        "NFLX": 0.10,
        "MSFT": 0.15,
        "AMZN": 0.20
    }
    colors = {
        "GOOG": "blue",
        "AAPL": "red",
        "NFLX": "green",
        "MSFT": "orange",
        "AMZN": "purple"
    }

    fig = go.Figure()

    for stock in stocks:
        df, initial = fetch_and_normalize(stock, period, interval)
        n = len(df)
        if n < actual_points:
            continue

        # Extract the last 'actual_points' data points as actual data.
        df_actual = df.iloc[-actual_points:]
        x_actual = np.arange(actual_points)  # 0..actual_points-1
        y_offset = offsets.get(stock, 0)
        y_actual = np.full(actual_points, y_offset)
        z_actual = df_actual['Normalized'].values

        # Plot actual data (solid line).
        fig.add_trace(go.Scatter3d(
            x=x_actual,
            y=y_actual,
            z=z_actual,
            mode='lines',
            line=dict(color=colors.get(stock, "gray"), width=4),
            name=f"{stock} Actual"
        ))

        # Generate multiple predictions.
        pred = generate_future_projections_pattern(
            stock, interval, future_points=pred_points, num_lines=num_pred_lines)
        for pred_line in pred:
            pred_data = pred_line['data']
            # Normalize predicted prices using the same initial.
            z_pred = np.array([item['close'] for item in pred_data]) / initial
            # The predicted line should start exactly where the actual line ends (x=actual_points-1).
            L = len(z_pred)
            x_pred = np.arange(actual_points - 1, actual_points - 1 + L)
            y_pred = np.full(L, y_offset)

            fig.add_trace(go.Scatter3d(
                x=x_pred,
                y=y_pred,
                z=z_pred,
                mode='lines',
                line=dict(color=colors.get(stock, "gray"),
                          width=4, dash='dot'),
                showlegend=False  # No separate legend label for predictions
            ))

    # Set default camera orientation
    fig.update_layout(
        width=1000,     # Increase width
        height=700,     # Increase height
        scene=dict(
            xaxis_title="Time Index",
            yaxis_title="Offset",
            zaxis_title="Normalized Price"
        ),
        scene_camera=dict(
            eye=dict(x=-1.5, y=-2.5, z=0.8)
        ),
        # Remove extra margins if you want a tighter fit
        margin=dict(l=0, r=0, t=0, b=0)
    )

    return fig


def render_3d_predictions_tab():
    st.header("3D Predictions Comparison")
    st.write("For each stock, the last 10 periods of actual data are shown as a solid line. The predicted next 5 periods (for each available pattern) are overlaid as dotted lines in the same color. The camera is tilted by default for a better view.")

    stocks = ["GOOG", "AAPL", "NFLX", "MSFT", "AMZN"]
    fig = plot_3d_predictions(
        stocks,
        period="1y",
        interval="1d",
        actual_points=10,
        pred_points=5,
        num_pred_lines=5
    )
    st.plotly_chart(fig)


if __name__ == "__main__":
    render_3d_predictions_tab()
