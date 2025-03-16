import streamlit as st
from predefined_tab import render_predefined_tab
from custom_tab import render_custom_tab
from backtest_tab import render_backtest_tab
from three_d_predictions_tab import render_3d_predictions_tab, plot_3d_predictions
import etf_config  # This file contains ETF_CONFIG

st.title("Instrument Analysis App")

# Existing tabs
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

# Dynamically generate ETF 3D Predictions tabs
if hasattr(etf_config, "ETF_CONFIG") and etf_config.ETF_CONFIG:
    st.header("ETF 3D Predictions")
    # Get ETF names from the config dictionary
    etf_dict = etf_config.ETF_CONFIG
    etf_tab_names = list(etf_dict.keys())
    etf_tabs_container = st.tabs(etf_tab_names)
    for i, etf_name in enumerate(etf_tab_names):
        with etf_tabs_container[i]:
            st.subheader(f"3D Predictions for {etf_name}")
            # Use the ETF's component list from the config
            components = etf_dict[etf_name]
            fig = plot_3d_predictions(
                components, 
                period="1y", 
                interval="1d", 
                actual_points=10, 
                pred_points=5, 
                num_pred_lines=5
            )
            st.plotly_chart(fig)

if __name__ == "__main__":
    st.write("Ready to analyze instruments!")
