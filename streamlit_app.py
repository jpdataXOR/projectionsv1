import streamlit as st
from predefined_tab import render_predefined_tab
from custom_tab import render_custom_tab
from backtest_tab import render_backtest_tab
# from three_d_tab import render_3d_tab  # REMOVE THIS
from three_d_predictions_tab import render_3d_predictions_tab

st.title("Instrument Analysis App")

# Create four or five tabs:
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
# with tab4:
#     render_3d_tab()  # REMOVE THIS
with tab4:
    render_3d_predictions_tab()

if __name__ == "__main__":
    st.write("Ready to analyze instruments!")
