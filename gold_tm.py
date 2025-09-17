import requests
from bs4 import BeautifulSoup

def get_gold_rates():

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
    return data_gold
if __name__ == "__main__":
    rates = get_gold_rates()
    for metal, rate in rates.items():
         print(f"{metal}: {rate}")