import requests

url = "https://yahoo-finance127.p.rapidapi.com/price/eth-usd"

headers = {
	"X-RapidAPI-Key": "939ce84536msh799a985451fb0e5p17478cjsn1e1d09427bab",
	"X-RapidAPI-Host": "yahoo-finance127.p.rapidapi.com"
}

response = requests.get(url, headers=headers)

print(response.json())