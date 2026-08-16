import urllib.request

url = "http://localhost:8000/api/v1/transactions/reset"
req = urllib.request.Request(url, method="DELETE")
try:
    resp = urllib.request.urlopen(req)
    print("Reset response:", resp.read().decode())
except Exception as e:
    print("Failed to reset:", e)
