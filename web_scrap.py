import requests
from bs4 import BeautifulSoup

url = 'https://www.barchart.com/stocks/quotes/$HIGQ/overview'

response = requests.get(url)

# print(response.text)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    net_highs = soup.find_all(class_ = "show-for-large-up")

print(net_highs)