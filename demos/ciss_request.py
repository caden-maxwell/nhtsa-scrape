import requests

url = "https://crashviewer.nhtsa.dot.gov/CISS/CISSCrashData/?crashId=6028"

response = requests.get(url)
print(response.text)
