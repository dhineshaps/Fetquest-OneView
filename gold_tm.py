import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
gold_data = []

@st.cache_data
def get_gold_rates(gold_list):

    url = st.secrets["tml_link"]
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
