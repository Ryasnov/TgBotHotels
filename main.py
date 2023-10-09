import requests
from pprint import pprint

"""locations/search (Deprecated)"""

url = "https://hotels4.p.rapidapi.com/locations/search"

querystring = {"query":"grozny","locale":"en_US"}

headers = {
	"X-RapidAPI-Key": "e63af22e92msh9f446d4dfc9ba1ap1e570ajsn083b4c33848b",
	"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)
response = response.json()
dest_id = response['suggestions'][1]['entities'][0]['destinationId']
# 757810592

"""properties/list (Deprecated)"""
url = "https://hotels4.p.rapidapi.com/properties/list"

querystring = {"destinationId":dest_id,"pageNumber":"1","pageSize":"5","checkIn":"2023-11-25","checkOut":"2023-11-27","adults1":"1","sortOrder":"PRICE","locale":"ru_RU","currency":"USD"}

headers = {
	"X-RapidAPI-Key": "e63af22e92msh9f446d4dfc9ba1ap1e570ajsn083b4c33848b",
	"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

pprint(response)
