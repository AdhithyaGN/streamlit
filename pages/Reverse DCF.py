import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title("Reverse DCF")

#left_column, right_column = st.columns(2)

nse_bse_symbol=st.text_input("NSE/BSE symbol")

url = f"https://www.screener.in/company/{nse_bse_symbol}/"

response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')

    ratios_div = soup.find('div', class_='company-ratios')
    ratios_list = ratios_div.find_all('li')
    for ratio in ratios_list:
        name = ratio.find('span', class_='name').text.strip()  
        
        if name=="Stock P/E":
            pe_ratio= ratio.find('span', class_='number').text.strip()

        if name=="Market Cap":
            market_cap=ratio.find('span', class_='number').text.strip()
    st.write(f"Current PE:{pe_ratio}")

    balance_sheet_section = soup.find('section', id='profit-loss')
    table = balance_sheet_section.find('table', class_='data-table responsive-text-nowrap')
    headers = [th.text.strip() for th in table.find_all('th')[1:]]
    data = []
    for row in table.find_all('tr')[1:]:  # Skip the first row with headers
        # Extract the button element for the row label (e.g., "Net Profit")
        button = row.find('button', class_='button-plain')
        if button:
            row_label = button.text.strip().replace('\u00a0', '')  # Clean the label text by removing non-breaking spaces
        else:
            continue  # Skip rows that don't have the button

        # Extract the data for the row
        row_values = [td.text.strip() for td in row.find_all('td')[1:]]  # Skip the first <td> containing the button

        # Append the row to the data list
        data.append([row_label] + row_values)

    # Step 5: Convert to a DataFrame
    df = pd.DataFrame(data, columns=["Metric"] + headers)
    fy23_netprofit=df.loc[df['Metric'] == 'Net Profit+', 'Mar 2024']
    fy23_netprofit_cleaned = fy23_netprofit.apply(lambda x: int(x.replace(',', '')) if ',' in str(x) else int(x))
    def comma_remover(string):
        if "," in string:
            string=string.replace(",","")
        return int(string)
    
    fy23_pe=round((comma_remover(market_cap)/fy23_netprofit_cleaned),1).values[0]
    st.write(f'FY23 PE : {fy23_pe}')

    ratios_section = soup.find('section', id='ratios')
    table1 = ratios_section.find('table', class_='data-table responsive-text-nowrap')
    headers1 = [th.text.strip() for th in table1.find_all('th')][1:]
    data = []
    for row in table1.find_all('tr')[1:]:
        row_values = [td.text.strip() for td in row.find_all('td')[1:]]
        row_label = row.find('td').text.strip()
        data.append([row_label] + row_values)
    df = pd.DataFrame(data, columns=["Metric"] + headers1)
    ROCE_list=[df.loc[df['Metric']=='ROCE %','Dec 2019'],df.loc[df['Metric']=='ROCE %','Dec 2020'],df.loc[df['Metric']=='ROCE %','Dec 2021'],
               df.loc[df['Metric']=='ROCE %','Dec 2022'],df.loc[df['Metric']=='ROCE %','Dec 2023']]
    roce_cleaned_list=[]
    for i in ROCE_list:
        
        i=i.apply(lambda x: int(x.replace("%","")) if "%" in str(x) else int(x))
        roce_cleaned_list.append(i)
    st.write(f"5-yr median pre-tax RoCE :{round(np.median(roce_cleaned_list))}%")

    tables = soup.find_all('table', class_='ranges-table')

    sales_data = []
    profit_data = []
    for table in tables:
        header = table.find('th').get_text(strip=True)
        
        rows = table.find_all('tr')[1:]  # Skip the header row
        
        if 'Sales Growth' in header:
            for row in rows:
                cells = row.find_all('td')
                if len(cells) == 2:
                    label = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True).replace('%', '')
                    sales_data.append([label, float(value)])
                    
        elif 'Profit Growth' in header:
            for row in rows:
                cells = row.find_all('td')
                if len(cells) == 2:
                    label = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True).replace('%', '')
                    profit_data.append([label, float(value)])

    data_growth={
    "":["Sales Growth","Profit Growth"],
    "10 YRS":[sales_data[0][1],profit_data[0][1]],
    "5 YRS":[sales_data[1][1],profit_data[1][1]],
    "3 YRS":[sales_data[2][1],profit_data[2][1]],
    "TTM":[sales_data[3][1],profit_data[3][1]],
}
    df = pd.DataFrame(data_growth)
    st.table(df)

    plot_df=df.transpose()
    plot_df.columns=plot_df.iloc[0]
    plot_df=plot_df[1:]
    

    fig1,ax1=plt.subplots()
    ax1.bar(plot_df.index,plot_df["Sales Growth"],color='lightblue')
    ax1.set_xlabel("Time Period")
    ax1.set_ylabel("Sales Growth")
    fig2,ax2=plt.subplots()
    ax2.bar(plot_df.index,plot_df["Profit Growth"],color='lightblue')
    ax2.set_xlabel("Time Period")
    ax2.set_ylabel("Profit Growth")


    st.pyplot(fig1)
    st.pyplot(fig2)


    






coc = st.slider('Cost of Capital (CoC) in %', min_value=8, max_value=16, step=1)
st.write(f'You selected CoC: {coc}%')

roce = st.slider('Return on Capital Employed (RoCE) in %', min_value=10, max_value=100, step=5)
st.write(f'You selected RoCE: {roce}%')

growth_rate = st.slider('Growth during high growth period in %', min_value=8, max_value=20, step=1)
st.write(f'You selected Growth rate: {growth_rate}%')

high_growth_period = st.slider('High growth period (years)', min_value=10, max_value=25, step=1)
st.write(f'You selected High growth period: {high_growth_period} years')

fade_period = st.selectbox('Fade period (years)', options=[5, 10, 15, 20])
st.write(f'You selected Fade period: {fade_period} years')

terminal_growth_rate = st.slider('Terminal growth rate in %', min_value=0.0, max_value=7.5, step=0.5)
st.write(f'You selected Terminal growth rate: {terminal_growth_rate}%')

submit=st.button("Calculate Intrinsic P/E")
if submit:

    RoC=roce/100
    Tax_Rate=0.25
    RoC_posttax=RoC*(1-Tax_Rate)
    CoC=coc/100
    Earnings_growth_15_years=growth_rate/100
    growth_period=high_growth_period
    fade_period=fade_period
    Terminal_growth_rate=terminal_growth_rate/100
    Reinvestment_rate1=Earnings_growth_15_years/RoC_posttax
    Reinvestment_rate2=Terminal_growth_rate/RoC_posttax

    Year=[x for x in range(-1,growth_period+fade_period+1)]

    initialiser1=0
    initialiser2=100
    Earnings_growth_rate={}
    EBT={}
    NOPAT={}
    Capital_ending={}
    Investment={}
    FCF={}
    Discount_factor={}
    Discounted_FCF={}
    for i in Year:
        
        Earnings_growth_rate[i]=initialiser1
        EBT[i]=initialiser1
        NOPAT[i]=initialiser1
        Capital_ending[i]=initialiser2
        Investment[i]=initialiser1
        FCF[i]=initialiser1
        Discount_factor[i]=initialiser1
        Discounted_FCF[i]=initialiser1


    NOPAT[0]=Capital_ending[-1]*RoC_posttax

    Investment[0]=NOPAT[0]*Reinvestment_rate1

    Capital_ending[0]=Capital_ending[-1]+Investment[0]

    EBT[0]=NOPAT[0]/(1-Tax_Rate)


    FCF[0]=NOPAT[0]-Investment[0]


    for i in range(1,growth_period+1):
        NOPAT[i]=Capital_ending[i-1]*RoC_posttax
        Investment[i]=NOPAT[i]*Reinvestment_rate1
        Capital_ending[i]=Capital_ending[i-1]+Investment[i]
        FCF[i]=NOPAT[i]-Investment[i]
        Earnings_growth_rate[i]=NOPAT[i]/NOPAT[i-1]-1

    for i in range(growth_period+1,growth_period+fade_period+1):
        Earnings_growth_rate[i]=Earnings_growth_rate[i-1]-(Earnings_growth_15_years-Terminal_growth_rate)/fade_period
        NOPAT[i]=Capital_ending[i-1]*RoC_posttax
        Investment[i]=Earnings_growth_rate[i]/RoC_posttax*NOPAT[i]
        Capital_ending[i]=Capital_ending[i-1]+Investment[i]
        FCF[i]=NOPAT[i]-Investment[i]


    Discount_factor={}
    Discounted_FCF={}
    for i in range(growth_period+fade_period+1):
        EBT[i]=NOPAT[i]/(1-Tax_Rate)
        Discount_factor[i]=1/(1+CoC)**i
        Discounted_FCF[i]=Discount_factor[i]*FCF[i]

    Terminal_NOPAT=NOPAT[growth_period+fade_period]*(1+Terminal_growth_rate)/(CoC-Terminal_growth_rate)

    Terminal_Investment=Terminal_NOPAT*Reinvestment_rate2


    Terminal_FCF=Terminal_NOPAT-Terminal_Investment

    Terminal_DiscountFactor=Discount_factor[growth_period+fade_period]

    Terminal_Discounted_FCF=Terminal_FCF*Terminal_DiscountFactor

    Intrinsic_value=sum(Discounted_FCF.values(),Terminal_Discounted_FCF)

    Intrinsic_PE=Intrinsic_value/NOPAT[0]

    st.write(f"Intrinsic P/E:  {round(Intrinsic_PE,2)}")

    


