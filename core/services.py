import requests


def get_data(url):
    params = {}
    r = requests.get(url, params=params)
    data = r.json()
    return data