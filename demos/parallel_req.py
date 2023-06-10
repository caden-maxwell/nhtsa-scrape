# Request Parallelization Demo

import concurrent.futures
import requests
import time

def fetch_url(url):
    timeout = 5
    print(f"Fetching {url}...")
    start = time.time()
    response = requests.get(url, timeout=timeout)
    end = time.time()
    if end - start >= timeout:
        print(f"Fetching {url} took too long.")
    else:
        print(f"Fetched {url} with status code {response.status_code} in {end-start:.2f} seconds")
    return response.text

urls = ['https://crashviewer.nhtsa.dot.gov/nass-cds/CaseForm.aspx?xsl=main.xsl&CaseID=151007322','https://crashviewer.nhtsa.dot.gov/nass-cds/CaseForm.aspx?xsl=main.xsl&CaseID=151007322','https://crashviewer.nhtsa.dot.gov/nass-cds/CaseForm.aspx?xsl=main.xsl&CaseID=151007322',]
# urls = ['https://www.example.com', 'https://www.google.com', 'https://www.github.com', 'https://www.stackoverflow.com', 'https://www.python.org', 'https://www.youtube.com', 'https://www.reddit.com', 'https://www.netflix.com', 'https://www.amazon.com', 'https://www.wikipedia.org', 'https://www.facebook.com', 'https://www.twitter.com', 'https://www.instagram.com', 'https://www.linkedin.com', 'https://www.pinterest.com', 'https://www.tumblr.com', 'https://www.microsoft.com', 'https://www.apple.com', 'https://www.yahoo.com', 'https://www.bing.com', 'https://www.paypal.com', 'https://www.ebay.com', 'https://www.aliexpress.com', 'https://www.wordpress.com', 'https://www.imgur.com', 'https://www.imdb.com', 'https://www.espn.com', 'https://www.cnn.com', 'https://www.nytimes.com', 'https://www.bbc.com', 'https://www.craigslist.org', 'https://www.walmart.com', 'https://www.target.com', 'https://www.bestbuy.com', 'https://www.lowes.com', 'https://www.etsy.com', 'https://www.newegg.com', 'https://www.alibaba.com']


print("Request Parallelization Demo\n")
print("Using Parallel Requests:")
start = time.time()
with concurrent.futures.ThreadPoolExecutor() as executor:
    # Submit the requests concurrently
    futures = [executor.submit(fetch_url, url) for url in urls]

    # Gather the results as they complete
    results = [future.result() for future in concurrent.futures.as_completed(futures)]

end = time.time()
print(f"All responses received. Time taken: {end-start:.2f}s\n")

print("Using Sequential Requests:")
start2 = time.time()
for url in urls:
    response = fetch_url(url)
end2 = time.time()
print(f"All responses received. Time taken: {end2-start2:.2f}s\n")

print(f"Using parallel requests was {(end2-start2)/(end-start):.2f} times faster than using sequential requests.")