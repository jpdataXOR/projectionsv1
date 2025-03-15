# data_utils.py
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

def get_stock_data(stock_symbol, interval):
    """Fetches stock data from yfinance."""
    period = "1y" if interval == "1h" else "5y" if interval == "1d" else "max"
    
    instrument = yf.Ticker(stock_symbol)
    array_data = instrument.history(period=period, interval=interval, auto_adjust=False)
    date_format = '%d-%b-%Y %H:%M' if interval == "1h" else '%d-%b-%Y'
    
    stock_data = [{
        'date': array_data.index[i].strftime(date_format),
        'close': array_data.iloc[i]['Close']
    } for i in range(len(array_data))]
    
    return stock_data

def generate_future_projections(stock_data, future_points=10, num_lines=5):
    """
    Generates future projection lines based on the last data point.
    Each future point applies a random percentage change between -1% and +1%.
    The first future point duplicates the last actual data to avoid any gap.
    """
    last_real_price = stock_data[-1]['close']
    last_real_date = datetime.strptime(stock_data[-1]['date'], '%d-%b-%Y')
    future_data = []
    
    for _ in range(num_lines):
        future_line = []
        current_price = last_real_price
        current_date = last_real_date
        
        # Duplicate last real point to ensure continuity
        future_line.append({
            'date': current_date.strftime('%d-%b-%Y'),
            'close': current_price
        })
        
        for _ in range(future_points):
            change_percentage = np.random.uniform(-1, 1)
            current_price *= (1 + change_percentage / 100)
            current_date += timedelta(days=1)  # Assuming daily intervals
            future_line.append({
                'date': current_date.strftime('%d-%b-%Y'),
                'close': current_price
            })
        
        future_data.append(future_line)
    
    return future_data

def highlight_cells(val):
    """Returns a CSS style string for background color based on cell value."""
    # Green for positive, Red for negative. Intensity is proportional to abs(val)
    intensity = min(abs(val) / 5, 1)  # Normalize intensity (0 to 1)
    if val > 0:
        # Green: use 0 for red, 255 for green.
        return f'background-color: rgba(0, 255, 0, {intensity})'
    else:
        # Red: use 255 for red, 0 for green.
        return f'background-color: rgba(255, 0, 0, {intensity})'

def prepare_table(stock_data):
    """
    Prepares and styles a DataFrame for the last 10 actual data points.
    Shows the percentage change for each period (color-coded).
    """
    # Calculate percentage change for the last 10 data points.
    df = pd.DataFrame(stock_data[-10:])
    # Calculate percentage change column: (% change from previous close)
    df['percentage_change'] = df['close'].pct_change() * 100
    df['percentage_change'] = df['percentage_change'].round(2)
    
    # Remove the first row since it doesn't have a valid percentage change
    df = df.iloc[1:]
    # Use 'date' as index and only keep the percentage_change column.
    df = df[['date', 'percentage_change']].set_index('date')
    
    # Transpose to display dates as columns
    styled_df = df.T.style.applymap(highlight_cells)
    return styled_df
