import pandas as pd
from collections import defaultdict
import requests

url = "https://portal.amfiindia.com/spages/NAVAll.txt"

response = requests.get(url)
response.raise_for_status()

lines = response.text.splitlines()

cols_list = [x.strip() for x in lines if "Mutual Fund" in x]

funds_by_amc = defaultdict(list)
for x in lines:
    if ';' in x and 'Scheme Code' not in x:
        schme = x.split(";")[3].strip()
        house = schme.split(" ")[0]
        funds_by_amc[house].append(schme)


funds_by_amc_new = defaultdict(list)
for j in cols_list:
  for i in funds_by_amc.keys():
    new_val =j.split(" ")[0]
    if new_val == "Jio":
        new_val = "JioBlackRock"
    if new_val == "PPFAS":
        new_val = "Parag"
    if new_val == "Capitalmind":
        new_val ="CAPITALMIND"
    if new_val == "Angel":
        new_val ="ANGEL"
    if new_val == "Trust":
        new_val ="TRUSTMF"
    if i == new_val:
      for li in funds_by_amc.get(i):
        funds_by_amc_new[j].append(li)

df = pd.DataFrame.from_dict(funds_by_amc_new, orient="index").transpose()

df.to_csv("mf_funds.csv", index=False, encoding="utf-8")