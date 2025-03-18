import streamlit as st
from predefined_tab import render_predefined_tab
from custom_tab import render_custom_tab
from backtest_tab import render_backtest_tab
from three_d_predictions_tab import render_3d_predictions_tab, plot_3d_predictions
from data_utils import get_stock_data, generate_future_projections_pattern
from chart_utils import plot_stock_chart
import etf_config  # Contains ETF_CONFIG

st.title("Instrument Analysis App")

# Create main tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Predefined Stocks",
    "Custom Stock Search",
    "Backtest Predictions",
    "3D Predictions"
])

with tab1:
    render_predefined_tab()
with tab2:
    render_custom_tab()
with tab3:
    render_backtest_tab()
with tab4:
    render_3d_predictions_tab()

# ETF-Specific 3D Predictions & Normal Charts
if hasattr(etf_config, "ETF_CONFIG") and etf_config.ETF_CONFIG:
    st.header("ETF 3D Predictions & Projections")

    etf_dict = etf_config.ETF_CONFIG
    etf_names = list(etf_dict.keys())

    # Create tabs for each ETF
    etf_tabs_container = st.tabs(etf_names)
    
    for i, etf_name in enumerate(etf_names):
        with etf_tabs_container[i]:
            st.subheader(f"3D Predictions for {etf_name}")
            stocks_with_labels = etf_dict[etf_name]  # Format: [{"id": ..., "label": ...}]

            # Generate and show 3D Prediction Chart
            fig_3d = plot_3d_predictions(
                stocks_with_labels,
                period="1y",
                interval="1d",
                actual_points=10,
                pred_points=5,
                num_pred_lines=5
            )
            st.plotly_chart(fig_3d, key=f"{etf_name}_3d_chart")

            # Generate Normal Projection Charts for each instrument
            for index, stock_data in enumerate(stocks_with_labels):
                stock = stock_data["id"]
                label = stock_data["label"]

                st.subheader(f"Projections for {label} ({stock})")

                # Fetch historical data
                stock_history = get_stock_data(stock, interval="1d")

                # Generate future projections
                future_predictions = generate_future_projections_pattern(stock, interval="1d", future_points=5, num_lines=5)

                # Generate and display 2D projection chart with a unique key
                fig_2d = plot_stock_chart(stock_history, future_predictions, date_format="%d-%b-%Y")
                
                # Add a unique key using stock ID + index to avoid duplicates
                st.plotly_chart(fig_2d, key=f"{stock}_projection_{index}")

if __name__ == "__main__":
    st.write("Ready to analyze instruments!")
