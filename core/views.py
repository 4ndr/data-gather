import json
import requests

from django.shortcuts import render

# Create your views here.

def base(request):
    smartcitizen = requests.get('https://api.smartcitizen.me/v0/devices/world_map')
    smartcitizen_data = json.dumps(smartcitizen.json())

    lass = requests.get('https://pm25.lass-net.org/data/last-all-lass.json')
    lass_data = json.dumps(lass.json())

    openaq = requests.get('https://api.openaq.org/v1/measurements')
    openaq_data = json.dumps(openaq.json())

    data = {'data1': smartcitizen_data, 'data2': lass_data, 'data3': openaq_data, }
    return render(request, 'base.html', data)