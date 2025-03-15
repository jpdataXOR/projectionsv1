import streamlit as st
import yfinance as yf
import pandas as pd
import re
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Global variables
data_dic = {}
current_values = []

def get_stock_data(stock_symbol, interval):
    global data_dic, current_values

    # Set appropriate period based on interval
    period = "1y" if interval == "1h" else "5y" if interval == "1d" else "max"
    
    instrument = yf.Ticker(stock_symbol)
    array_data = instrument.history(period=period, interval=interval, auto_adjust=False)

    result_string = ''.join(['U' if array_data.iloc[i]['Close'] >= array_data.iloc[i-1]['Close'] else 'D'
                             for i in range(1, len(array_data))])

    array_data = array_data.iloc[::-1]
    result_string = result_string[::-1]

    index_dict = {}
    for iteration in range(8, 5, -1):
        string_to_match = result_string[0:iteration]
        indices = [index.start() for index in re.finditer(string_to_match, result_string)]
        if len(indices) > 2:
            for matched_index in indices[1:]:
                if matched_index not in index_dict:
                    index_dict[matched_index] = len(string_to_match)

    for key, value in index_dict.items():
        indices, matched, future_average = print_difference_data(array_data, key, value, 13)
        index_dict[key] = (value, indices, matched, future_average)

    # Format string based on interval
    date_format = '%d-%b-%Y %H:%M' if interval == "1h" else '%d-%b-%Y'
    
    # Get last 8 values for current values and past prices
    current_values = [{
        'date': array_data.iloc[count].name.strftime(date_format),
        'close': array_data.iloc[count]['Close'],
        'percentage_difference': ((array_data.iloc[count]['Close'] - array_data.iloc[count+1]['Close']) /
                                  array_data.iloc[count+1]['Close']) * 100
    } for count in range(8)]

    # Get past prices
    past_prices = [{
        'date': array_data.iloc[count].name.strftime(date_format),
        'close': array_data.iloc[count]['Close'],
        'percentage_difference': ((array_data.iloc[count]['Close'] - array_data.iloc[count+1]['Close']) /
                                  array_data.iloc[count+1]['Close']) * 100
    } for count in range(8, 16)]

    return index_dict, current_values, past_prices

def print_difference_data(arg_array, index, matched_length, forward_length):
    matched = [{
        'date': arg_array.iloc[count].name.strftime('%d-%b-%Y %H:%M'),
        'close': arg_array.iloc[count]['Close'],
        'percentage_difference': ((arg_array.iloc[count]['Close'] - arg_array.iloc[count+1]['Close']) /
                                  arg_array.iloc[count+1]['Close']) * 100
    } for count in range(index, index + matched_length)]

    indices = [{
        'date': arg_array.iloc[count].name.strftime('%d-%b-%Y %H:%M'),
        'close': arg_array.iloc[count]['Close'],
        'percentage_difference': ((arg_array.iloc[count-1]['Close'] - arg_array.iloc[count]['Close']) /
                                  arg_array.iloc[count]['Close']) * 100
    } for count in range(index, index - forward_length, -1)]

    future_average = sum(index['percentage_difference']
                         for index in indices) / len(indices)
    return indices, matched, future_average

def main():
    st.title("Stock Analysis App")

    # Mapping of meaningful names to stock symbols
    stock_options = {
        "Australian Stock Exchange": "^AXJO",
        "NASDAQ 100": "^NDX",
        "Bitcoin": "BTC-USD",
        "Nikkei 225 - Japan": "^N225",
        "Hang Seng - Hong Kong": "^HSI",
        "FTSE 100 - UK": "^FTSE",
        "DAX - Germany": "^GDAXI",
        "CAC 40 - France": "^FCHI",
        "S&P 500 - US": "^GSPC",
        "Toronto Stock Exchange": "^GSPTSE",
        "NIFTY 50 - India": "^NSEI",
        "IBEX 35 - Spain": "^IBEX",
        "AEX - Netherlands": "^AEX",
        "FTSE MIB - Italy": "^FTSEMIB",
        "Bovespa - Brazil": "^BVSP",
        "IPC - Mexico": "^MEXBOL",
        "Volatility Index (VIX)": "^VIX",
        "USD/CHF": "USDCHF=X",
        "USD/JPY": "USDJPY=X",
        "AUD/USD": "AUDUSD=X",
        "EUR/USD": "EURUSD=X",
        "iShares Semiconductor ETF": "SOXX"  # SOXX ETF with clean name
    }


    selected_stock = st.selectbox("Select a stock or index", list(stock_options.keys()))
    selected_symbol = stock_options[selected_stock]
    selected_interval = st.selectbox("Select an interval", ["1d", "1h", "1wk"])
    
    if selected_interval == "1wk":
        selected_interval = "1wk"

    if st.button("Analyze"):
        try:
            data_dic, current_values, past_prices = get_stock_data(selected_symbol, selected_interval)

            st.info(f"Analyzing: {selected_stock}")

            dates = [datetime.strptime(data['date'], '%d-%b-%Y') for data in current_values]
            current_prices = [data['close'] for data in current_values]
            current_trace = go.Scatter(x=dates, y=current_prices, mode='lines+markers',
                                       name='Current Stock Prices', marker=dict(color='blue'))
            fig_current = go.Figure(data=[current_trace])
            fig_current.update_layout(
                title="Current Stock Prices",
                xaxis_title="Date",
                yaxis_title="Price",
                showlegend=False
            )
            st.plotly_chart(fig_current)

            current_df = pd.DataFrame(current_values)
            st.dataframe(current_df)

        except Exception as e:
            st.error(f"Error analyzing stock: {e}")
            st.info("This could be due to an invalid ticker symbol or no data available for the selected interval.")

if __name__ == "__main__":
    main()
