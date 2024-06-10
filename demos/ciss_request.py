import requests

url = "https://crashviewer.nhtsa.dot.gov/CISS/SearchFilter"

response = requests.get(url)
print(response.text)
