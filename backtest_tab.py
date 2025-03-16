# backtest_tab.py
import streamlit as st
import yfinance as yf
import pandas as pd
import re
from datetime import datetime, timedelta
import plotly.graph_objects as go
from data_utils import generate_future_projections_pattern

def run_backtest_for_interval(symbol, interval, offset, future_points=10):
    """
    Simulate a past prediction by truncating the historical data by 'offset' periods.
    offset=0 means current prediction; offset=5 means simulate prediction 5 periods ago; etc.
    Returns:
        predicted_line: list of dicts for the predicted future (using the prediction algorithm).
        actual_line: list of dicts for the actual future data from full history.
    """
    period = "1y" if interval == "1h" else "5y" if interval == "1d" else "max"
    instrument = yf.Ticker(symbol)
    df_full = instrument.history(period=period, interval=interval, auto_adjust=False)
    df_full = df_full.sort_index()  # Ensure ascending order
    
    # Truncate data to simulate a prediction made in the past
    if offset > 0:
        df_truncated = df_full.iloc[:-offset]
    else:
        df_truncated = df_full
    
    # Use the modified prediction function with our truncated data.
    predicted = generate_future_projections_pattern(symbol, interval, future_points=future_points, num_lines=1, data_override=df_truncated)
    predicted_line = predicted[0]['data']
    
    # Extract the actual future data from the full DataFrame
    last_time = df_truncated.index[-1]
    df_future = df_full[df_full.index >= last_time].iloc[:future_points+1]
    date_format = '%d-%b-%Y %H:%M' if interval=="1h" else '%d-%b-%Y'
    actual_line = [{'date': idx.strftime(date_format), 'close': row['Close']} for idx, row in df_future.iterrows()]
    
    return predicted_line, actual_line

def plot_backtest_chart(predicted_line, actual_line, interval):
    """
    Plots an overlay chart with:
      - Predicted future data (white dashed line)
      - Actual future data (blue dashed line)
    """
    date_format = '%d-%b-%Y %H:%M' if interval=="1h" else '%d-%b-%Y'
    predicted_dates = [datetime.strptime(item['date'], date_format) for item in predicted_line]
    predicted_prices = [item['close'] for item in predicted_line]
    
    actual_dates = [datetime.strptime(item['date'], date_format) for item in actual_line]
    actual_prices = [item['close'] for item in actual_line]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=predicted_dates,
        y=predicted_prices,
        mode='lines',
        line=dict(dash='dot', color='white'),
        name='Predicted'
    ))
    fig.add_trace(go.Scatter(
        x=actual_dates,
        y=actual_prices,
        mode='lines',
        line=dict(dash='dash', color='blue'),
        name='Actual'
    ))
    fig.update_layout(
        title="Backtest Prediction vs. Actual",
        xaxis_title="Date",
        yaxis_title="Price",
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white'
    )
    return fig

def render_backtest_tab():
    st.header("Backtest Prediction Evaluation")
    from stock_options import stock_options
    selected_stock = st.selectbox("Select a stock or index for Backtest", list(stock_options.keys()))
    if selected_stock:
        symbol = stock_options[selected_stock]
        st.info(f"Backtesting for: {selected_stock}")
        intervals = ["1wk", "1d", "1h"]
        offsets = [0, 5, 10]  # 0 = current, 5 = 5 periods ago, 10 = 10 periods ago
        for interval in intervals:
            st.subheader(f"Interval: {interval}")
            for offset in offsets:
                st.markdown(f"**Prediction simulated {offset} periods ago:**")
                try:
                    predicted_line, actual_line = run_backtest_for_interval(symbol, interval, offset)
                    fig = plot_backtest_chart(predicted_line, actual_line, interval)
                    st.plotly_chart(fig)
                except Exception as e:
                    st.error(f"Error in backtest for offset {offset}: {e}")
