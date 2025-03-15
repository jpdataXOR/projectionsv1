# chart_utils.py
import plotly.graph_objects as go
from datetime import datetime

def plot_stock_chart(stock_data, future_projections):
    """
    Plots a step line chart for the actual stock prices (last 10 data points)
    and overlays future projection lines with a dashed style.
    """
    # Convert the last 10 actual data points for plotting
    dates_actual = [datetime.strptime(data['date'], '%d-%b-%Y') for data in stock_data[-10:]]
    prices_actual = [data['close'] for data in stock_data[-10:]]
    
    # Create the figure and add actual stock prices
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates_actual,
        y=prices_actual,
        mode='lines',
        line_shape='hv',
        name='Stock Prices',
        marker=dict(color='blue')
    ))
    
    # Add each future projection line
    for proj in future_projections:
        future_dates = [datetime.strptime(data['date'], '%d-%b-%Y') for data in proj]
        future_prices = [data['close'] for data in proj]
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=future_prices,
            mode='lines',
            line_shape='hv',
            name='Future Projection',
            line=dict(dash='dot')
        ))
    
    # Update layout
    fig.update_layout(
        title="Stock Prices with Future Projections",
        xaxis_title="Date",
        yaxis_title="Price",
        showlegend=True
    )
    
    return fig
