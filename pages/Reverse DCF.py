import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from web_scrapper import screener_webscrapping
from DCF_calculator import dcf_calculation

st.title("Reverse DCF")

st.title("VALUING CONSISTENT COMPOUNDERS")

st.write("Hi there!")
st.write("This page will help you calculate intrinsic PE of consistent compounders through growth-RoCE DCF model.")
st.write("We then compare this with current PE of the stock to calculate degree of overvaluation.")



nse_bse_symbol=st.text_input("NSE/BSE symbol",value="NESTLEIND")

coc = st.slider('Cost of Capital (CoC) in %', min_value=8, max_value=16, step=1,value=12)
st.write(f'You selected CoC: {coc}%')

roce = st.slider('Return on Capital Employed (RoCE) in %', min_value=10, max_value=100, step=5,value=20)
st.write(f'You selected RoCE: {roce}%')

growth_rate = st.slider('Growth during high growth period in %', min_value=8, max_value=20, step=1,value=12)
st.write(f'You selected Growth rate: {growth_rate}%')

high_growth_period = st.slider('High growth period (years)', min_value=10, max_value=25, step=1,value=15)
st.write(f'You selected High growth period: {high_growth_period} years')

fade_period = st.selectbox('Fade period (years)', options=[5, 10, 15, 20],index=2)
st.write(f'You selected Fade period: {fade_period} years')

terminal_growth_rate = st.slider('Terminal growth rate in %', min_value=0.0, max_value=7.5, step=0.5,value=5.0)
st.write(f'You selected Terminal growth rate: {terminal_growth_rate}%')

submit=st.button("Calculate Intrinsic P/E")

if submit:
    screener_data=screener_webscrapping(nse_bse_symbol=nse_bse_symbol)
    dcf=dcf_calculation()
    

    url_check=screener_data.url_validation()

    if url_check!="Valid NSE/BSE Symbol":
        url=url_check

        screener_values=screener_data.Values_from_Screener(nse_bse_symbol)

        st.write(f"Stock Symbol: {nse_bse_symbol}")

        st.write(f"Current PE:{screener_data.pe_ratio}")

        st.write(f'FY23 PE : {screener_data.fy23_pe}')

        st.write(f"5-yr median pre-tax RoCE :{screener_data.fiveyr_median_roce}%")

        screener_plots=screener_data.Screener_table_and_plot(nse_bse_symbol)

        st.table(screener_data.dataframe)

        st.pyplot(screener_data.salesplot)
        st.pyplot(screener_data.profitplot)


        intrinsic_pe=dcf.intrinsic_pe(coc=coc,roce=roce,growth_rate=growth_rate,high_growth_period=high_growth_period,
                                      fade_period=fade_period,terminal_growth_rate=terminal_growth_rate)
        
        st.write(f"The calculated intrinsic PE is:  {dcf.intrinsic_pe_value}")

        deg_of_ov=dcf.degree_of_overvaluation(intrinsic_pe=intrinsic_pe,current_pe=screener_data.pe_ratio,fy23_pe=screener_data.fy23_pe)

        st.write(f"Degree Of Overvaluation : {deg_of_ov}%")
    else:
        st.write("Check the NSE/BSE Symbol")












        





    









    


