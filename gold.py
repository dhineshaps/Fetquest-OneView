import requests
from bs4 import BeautifulSoup

print("((((((((()))))))))")
def get_gold_rates():
    """
    Scrapes AngelOne gold rate page for 24K and 22K gold rates in INR (per 10g and per gram).
    """
    url = "https://www.angelone.in/gold-rates-today"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Find first row of table
    table = soup.find("tbody")
    first_row = table.find("tr")
    cells = first_row.find_all("td")

    gold_24k = cells[0].get_text(strip=True)
    gold_22k = cells[1].get_text(strip=True)

    # Convert to per gram (assuming per 10g shown)
    try:
        gold_24k_per_gram = round(int(gold_24k.replace(",", "")) / 10, 2)
        gold_22k_per_gram = round(int(gold_22k.replace(",", "")) / 10, 2)
    except:
        gold_24k_per_gram = gold_22k_per_gram = None

    return {
        "24K_per_10g": gold_24k,
        "22K_per_10g": gold_22k,
        "24K_per_gram": gold_24k_per_gram,
        "22K_per_gram": gold_22k_per_gram,
    }


# Example usage
if __name__ == "__main__":
    rates = get_gold_rates()
    print(rates)