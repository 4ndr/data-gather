import json

from django.shortcuts import render

# Create your views here.

def base(request):
    json_data1 = open('core/static/data/smartcitizen/world_map.json')
    json_data2 = open('core/static/data/lass/all_lass.json')
    json_data3 = open('core/static/data/openaq/measurements_1000.json')
    data1 = json.dumps(json.load(json_data1))
    data2 = json.dumps(json.load(json_data2))
    data3 = json.dumps(json.load(json_data3))
    data = {'data1': data1, 'data2': data2, 'data3': data3, }
    return render(request, 'base.html', data)