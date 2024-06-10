import requests

url = "https://crashviewer.nhtsa.dot.gov/SCI/GetvPICVehicleModelbyMake/?MakeIds=-1"

response = requests.get(url)
print(response.text)
