from django.shortcuts import render
from django.http import JsonResponse
import requests
import json


# Create your views here.
def show_map(request):
    template = 'map.html'
    return render(request, template)


def send_map_data(request, data_base):
    data_set = None
    if data_base == '1':
        smartcitizen = requests.get('https://api.smartcitizen.me/v0/devices/')
        data_set = json.dumps(smartcitizen.json())

    elif data_base == '2':
        lass = requests.get('https://pm25.lass-net.org/data/last-all-lass.json')
        data_set = json.dumps(lass.json())

    elif data_base == '3':
        openaq = requests.get('https://api.openaq.org/v1/measurements?limit=1000')
        data_set = json.dumps(openaq.json())

    data = {'data': data_set, }
    return JsonResponse(data)
