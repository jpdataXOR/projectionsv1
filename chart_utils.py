# chart_utils.py
import plotly.graph_objects as go
from datetime import datetime

def plot_stock_chart(stock_data, future_projections, date_format):
    """
    Plots a step line chart for the actual stock prices (last 8 data points)
    and overlays the future projection lines (from historical pattern logic).
    The predictions remain unchanged.
    """
    # Show only the last 8 actual prices
    dates_actual = [datetime.strptime(data['date'], date_format) for data in stock_data[-8:]]
    prices_actual = [data['close'] for data in stock_data[-8:]]
    
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

    # No scrolling, just start with 8 actual prices followed by predictions
    fig.update_layout(
        title="Stock Prices with Future Projections",
        xaxis_title="Date",
        yaxis_title="Price",
        showlegend=True
    )

    return fig
