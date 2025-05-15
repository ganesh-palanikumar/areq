import requests
import areq

response = areq.get("https://httpbin.org/get")
print(response.text)

response = requests.get("https://httpbin.org/get")
print(response.text)
