import pandas as pd
from collections import defaultdict
import requests

url = "https://portal.amfiindia.com/spages/NAVAll.txt"

response = requests.get(url)
response.raise_for_status()

lines = response.text.splitlines()

mf_list = {}
cols_list = [x.strip() for x in lines if "Mutual Fund" in x]

for x in lines:
   if "Mutual Fund" in x:
      if x in mf_list:
         mf_list[x] = mf_list[x] +  1
      else:
          mf_list[x] = 1
   
mf_real_list = []
for k in mf_list:
   mf_real_list.append(k)
print(mf_list)

print("*****************")
print(len(mf_list.keys()))

print(len(cols_list))
print("*****************")

funds_by_amc = defaultdict(list)
for x in lines:
    if ';' in x and 'Scheme Code' not in x:
        schme = x.split(";")[3].strip()
        house = schme.split(" ")[0]
        funds_by_amc[house].append(schme)

#print(funds_by_amc)

verify_list = []
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
      verify_list.append(i)
      for li in funds_by_amc.get(i):
        funds_by_amc_new[j].append(li)

df = pd.DataFrame.from_dict(funds_by_amc_new, orient="index").transpose()

# df.to_csv("funds1.csv", index=False, encoding="utf-8")

# mf_new = pd.read_csv('funds1.csv')
#column_names_index = mf_new .columns
column_names_index = df.columns
# print(len(column_names_index))
# mf_aums = st.selectbox("Mutual Fund", column_names_index)
# funds_name = mf_new[mf_aums] 
# fund_name = st.selectbox("Mutual Fund Scheme", funds_name, index=None)

# cols1,cols2 = st.columns(2)

# with cols1:
#    st.write(mf_real_list)
  
# with cols2:
#    st.write(list(column_names_index))


new_list = list(set(mf_real_list).difference(column_names_index))

print(new_list) ### to get the missing 