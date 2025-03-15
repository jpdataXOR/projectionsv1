# chart_utils.py
import plotly.graph_objects as go
from datetime import datetime

def plot_stock_chart(stock_data, future_projections, date_format):
    """
    Plots a step line chart for the actual stock prices (last 10 data points)
    and overlays the future projection lines (from historical pattern logic).
    Uses the provided date_format to parse date strings.
    """
    # Parse actual dates using the passed date_format
    dates_actual = [datetime.strptime(data['date'], date_format) for data in stock_data[-10:]]
    prices_actual = [data['close'] for data in stock_data[-10:]]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates_actual,
        y=prices_actual,
        mode='lines',
        line_shape='hv',
        name='Stock Prices',
        marker=dict(color='blue')
    ))
    
    for proj in future_projections:
        # Each projection is a dict with 'label' and 'data'
        future_line = proj['data']
        future_dates = [datetime.strptime(item['date'], date_format) for item in future_line]
        future_prices = [item['close'] for item in future_line]
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=future_prices,
            mode='lines',
            line_shape='hv',
            name=proj['label'],
            line=dict(dash='dot')
        ))
    
    fig.update_layout(
        title="Stock Prices with Future Projections",
        xaxis_title="Date",
        yaxis_title="Price",
        showlegend=True
    )
    return fig
