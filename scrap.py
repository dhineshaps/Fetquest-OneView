from bs4 import BeautifulSoup

import requests

url = "https://cse.google.com/cse?cx=002038729512466450040%3Amvqjrbqxynl#gsc.tab=0&gsc.q=java%20developer&gsc.sort="
response = requests.get(url)
#print(response.text)

soup = BeautifulSoup(response.text, 'html.parser')
print(soup.prettify())  # prints well-formatted HTML