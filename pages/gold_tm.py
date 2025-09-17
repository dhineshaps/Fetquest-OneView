import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd

gold_data = []

@st.cache_data
def get_gold_rates(gold_list):

    url = "https://www.thangamayil.com/scheme/index/rateshistory/"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    data = soup.find("div", class_= "columns")
    if not data:
        return {}
    
    data_1 = data.find("div", class_="history-rate card")
    if not data_1:
        return {}

    data_gold= {}
    containers = data_1.find_all("div", style=lambda x: x and "text-align: center" in x)

    for div in containers:
         price_tag = div.find("h2")
         type_tag = div.find("p")

         if price_tag and type_tag:
             price = price_tag.text.strip().replace("₹", "").replace(",", "")
             metal_type = type_tag.text.strip()
             data_gold[metal_type] = price
        
    
    for gold in gold_list:
        gold_type = f"Gold {gold}"
        curent_price =data_gold.get(gold_type)
        gold_data.append([gold,curent_price])

    
    df_gold_list = pd.DataFrame(gold_data, columns=["asset","Current price"])

    return df_gold_list 


# if __name__ == "__main__":
#     gold_list = ["22K","24k"]
#     rates = get_gold_rates(gold_list)
#     # for metal, rate in rates.items():
#     #      print(f"{metal}: {rate}")
#     # print(rates.get("Gold 22K"))
#     # print(rates.get("Gold 24K"))
# print(gold_data)

# gold_list = ["22K","24k"]
# print(get_gold_rates(gold_list))