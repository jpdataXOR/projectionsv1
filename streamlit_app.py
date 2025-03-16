import streamlit as st
from predefined_tab import render_predefined_tab
from custom_tab import render_custom_tab
from backtest_tab import render_backtest_tab

st.title("Instrument Analysis App")

# Create three tabs: Predefined Stocks, Custom Stock Search, and Backtest Predictions
tab1, tab2, tab3 = st.tabs(["Predefined Stocks", "Custom Stock Search", "Backtest Predictions"])

with tab1:
    render_predefined_tab()
with tab2:
    render_custom_tab()
with tab3:
    render_backtest_tab()

if __name__ == "__main__":
    st.write("Ready to analyze stocks!")
