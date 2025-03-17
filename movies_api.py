import requests

url = "https://api.themoviedb.org/3/search/movie?include_adult=false&language=en-US&page=1"

params = {
    "api_key": "Your api key",
    "query": "The Lion King"
}

response = requests.get(url=url, params=params)
data = response.json()["results"]

# original_title
# print(data)
for d in data:
    print(d["original_title"])








