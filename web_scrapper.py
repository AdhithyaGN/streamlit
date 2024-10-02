import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class screener_webscrapping:

    def __init__(self,nse_bse_symbol):
        self.nse_bse=nse_bse_symbol

    def url_validation(self):
        """
        This function under the screener_webscrapping class find the url is valid or not.

        """
        try:
            self.url=f"https://www.screener.in/company/{self.nse_bse}/"

            response = requests.get(self.url)

            if response.status_code == 200 :
                
                return "Valid NSE/BSE Symbol"
            else:
                return "Invalid NSE/BSE Symbol"
            
        except Exception as e:
            raise e
        
    def Values_from_Screener(self,url):
        """
        Values From Screener Function under the class screener_webscrapping can fetch the Current Stock P/E value,
        FY23 P/E, 5 Year Median ROCE%
          from the Screener site of any Stock Symbol


          ****note:The Market Cap and Net profit values are considered to be in Crores in Screener always.
        """
        self.url=f"https://www.screener.in/company/{self.nse_bse}/"
        try:
            
            response = requests.get(self.url)
            self.bs4_soup=BeautifulSoup(response.content, 'html.parser')

            ratios_div = self.bs4_soup.find('div', class_='company-ratios')

            ratios_list = ratios_div.find_all('li')

            for ratio in ratios_list:
                name = ratio.find('span', class_='name').text.strip()
                if name=="Stock P/E":
                    self.pe_ratio= ratio.find('span', class_='number').text.strip()

                if name=="Market Cap":
                    market_cap=ratio.find('span', class_='number').text.strip()

            balance_sheet_section = self.bs4_soup.find('section', id='profit-loss')

            table = balance_sheet_section.find('table', class_='data-table responsive-text-nowrap')
            headers = [th.text.strip() for th in table.find_all('th')[1:]]
            data = []
            for row in table.find_all('tr')[1:]:
                button = row.find('button', class_='button-plain')
                if button:
                    row_label = button.text.strip().replace('\u00a0', '')
                else:
                    continue

                row_values = [td.text.strip() for td in row.find_all('td')[1:]]

                data.append([row_label] + row_values)

            df = pd.DataFrame(data, columns=["Metric"] + headers)
            fy23_netprofit=df.loc[df['Metric'] == 'Net Profit+', 'Mar 2024']
            fy23_netprofit_cleaned = fy23_netprofit.apply(lambda x: int(x.replace(',', '')) if ',' in str(x) else int(x))

            def comma_remover(string):
                if "," in string:
                    string=string.replace(",","")
                    return int(string)
                
            self.market_cap=comma_remover(market_cap)

            self.fy23_pe=round((self.market_cap/fy23_netprofit_cleaned),1).values[0]


            ratios_section = self.bs4_soup.find('section', id='ratios')
            table1 = ratios_section.find('table', class_='data-table responsive-text-nowrap')
            headers1 = [th.text.strip() for th in table1.find_all('th')][1:]
            data1 = []
            for row in table1.find_all('tr')[1:]:
                row_values = [td.text.strip() for td in row.find_all('td')[1:]]
                row_label = row.find('td').text.strip()
                data1.append([row_label] + row_values)
            df1 = pd.DataFrame(data1, columns=["Metric"] + headers1)

            ROCE_list=[df1.iloc[5,len(df1.columns)-2],df1.iloc[5,len(df1.columns)-3],df1.iloc[5,len(df1.columns)-4],
                       df1.iloc[5,len(df1.columns)-5],df1.iloc[5,len(df1.columns)-6]]
            

            roce_cleaned_list=[]
            for i in ROCE_list:
                
                if "%" in str(i):
                    i=int(i.replace("%",""))
                else:
                    i=int(i)
    
    
                roce_cleaned_list.append(i)

            self.fiveyr_median_roce=round(np.median(roce_cleaned_list))

        except Exception as e:
            raise e
    

    def Screener_table_and_plot(self,url):

        """
        This function can fetch the compound sales growth and profit growth of 3,5,10 years tables and can show as Bar graphs
        """
        self.url=f"https://www.screener.in/company/{self.nse_bse}/"

        try:
            
            response = requests.get(self.url)
            self.bs4_soup=BeautifulSoup(response.content, 'html.parser')
            tables = self.bs4_soup.find_all('table', class_='ranges-table')
            sales_data = []
            profit_data = []
            for table in tables:
                header = table.find('th').get_text(strip=True)
                rows = table.find_all('tr')[1:]
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
            self.dataframe=df
            plot_df=self.dataframe.transpose()
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


            self.salesplot=fig1
            self.profitplot=fig2

        except Exception as e:
            raise e
        









    
            

            







    