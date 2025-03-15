# data_utils.py
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import re

def get_stock_data(stock_symbol, interval):
    """Fetches stock data from yfinance and returns a list of dictionaries (date, close)."""
    period = "1y" if interval == "1h" else "5y" if interval == "1d" else "max"
    instrument = yf.Ticker(stock_symbol)
    array_data = instrument.history(period=period, interval=interval, auto_adjust=False)
    date_format = '%d-%b-%Y %H:%M' if interval == "1h" else '%d-%b-%Y'
    stock_data = [{
        'date': array_data.index[i].strftime(date_format),
        'close': array_data.iloc[i]['Close']
    } for i in range(len(array_data))]
    return stock_data

def print_difference_data(arg_array, index, matched_length, forward_length):
    """
    Mimics the original logic: given a starting index and a matched pattern length,
    it extracts a sequence of future percentage differences from the DataFrame.
    """
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
    
    future_average = sum(item['percentage_difference'] for item in indices) / len(indices)
    return indices, matched, future_average

def generate_future_projections_pattern(stock_symbol, interval, future_points=10, num_lines=5):
    """
    Uses historical pattern matching logic to extract a series of future percentage changes
    from similar past patterns and projects future prices.
    Each projection is labeled with the date where the matching pattern was found.
    """
    period = "1y" if interval == "1h" else "5y" if interval == "1d" else "max"
    instrument = yf.Ticker(stock_symbol)
    array_data = instrument.history(period=period, interval=interval, auto_adjust=False)
    date_format = '%d-%b-%Y %H:%M' if interval == "1h" else '%d-%b-%Y'
    
    # Create a string of 'U' and 'D' representing Up/Down movements
    result_string = ''.join(['U' if array_data.iloc[i]['Close'] >= array_data.iloc[i-1]['Close'] else 'D'
                             for i in range(1, len(array_data))])
    # Reverse the data to mimic the original ordering
    array_data = array_data.iloc[::-1]
    result_string = result_string[::-1]
    
    index_dict = {}
    # Try pattern lengths from 8 down to 6
    for iteration in range(8, 5, -1):
        string_to_match = result_string[0:iteration]
        matches = [match.start() for match in re.finditer(string_to_match, result_string)]
        if len(matches) > 2:
            for matched_index in matches[1:]:
                if matched_index not in index_dict:
                    index_dict[matched_index] = len(string_to_match)
                    
    # For each pattern match, extract future percentage changes using print_difference_data
    data_dic = {}
    for key, value in index_dict.items():
        indices, matched, future_average = print_difference_data(array_data, key, value, 13)
        data_dic[key] = (value, indices, matched, future_average)
    
    # Get the last actual price and date from the raw data (data is reversed)
    last_row = array_data.iloc[0]
    last_close = last_row['Close']
    last_date = array_data.index[0]
    
    future_projections = []
    # Use the first num_lines patterns from data_dic
    for key in list(data_dic.keys())[:num_lines]:
        _, indices, matched, future_average = data_dic[key]
        # Extract future percentage returns from the first 'future_points' entries in indices
        future_returns = [item['percentage_difference'] / 100 for item in indices[:future_points]]
        future_prices = [last_close]
        for r in future_returns:
            future_prices.append(future_prices[-1] * (1 + r))
        # Build a future line with dates starting from last_date (duplicate last date to avoid a gap)
        future_line = []
        current_date = last_date
        future_line.append({'date': current_date.strftime(date_format), 'close': last_close})
        for price in future_prices[1:]:
            current_date += timedelta(days=1)  # Assuming daily interval for projections
            future_line.append({'date': current_date.strftime(date_format), 'close': price})
        
        # Label the projection with the date where the pattern was found
        match_date = array_data.index[key]
        label = f"Future Projection (Match Date: {match_date.strftime(date_format)})"
        
        future_projections.append({'label': label, 'data': future_line})
    
    return future_projections

def highlight_cells(val):
    """Returns a CSS style string for cell background based on the value."""
    intensity = min(abs(val) / 5, 1)
    if val > 0:
        return f'background-color: rgba(0, 255, 0, {intensity})'
    else:
        return f'background-color: rgba(255, 0, 0, {intensity})'

def prepare_table(stock_data):
    """
    Prepares and styles a DataFrame for the last 10 actual data points.
    Calculates the percentage change (from previous close) and applies color coding.
    """
    df = pd.DataFrame(stock_data[-10:])
    df['percentage_change'] = df['close'].pct_change() * 100
    df['percentage_change'] = df['percentage_change'].round(2)
    df = df.iloc[1:]
    df = df[['date', 'percentage_change']].set_index('date')
    styled_df = df.T.style.applymap(highlight_cells)
    return styled_df
