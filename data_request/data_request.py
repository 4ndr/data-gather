import requests
from mongoengine import connect

from map.models import SafeCastModel, SmartCitizenModel, SmartCitizenSensor, PurpleAirModel, PurpleAirReadings


def data_request_safecast():
    """
    request the safecast API and retrieve the data
    :return:
    """
    connect()
    safecast_api = requests.get('https://api.safecast.org/measurements.json?unit=PM2.5&unit=PM1&unit=PM10')
    safecast_data = safecast_api.json()
    count = 1

    for sc in safecast_data:
        print("%d de %d registros salvos" % (count, len(safecast_data)))
        safecast = SafeCastModel()
        safecast.self_load(sc)
        if safecast.self_validate():
            safecast.save()
        else:
            print("obj not saved")
        count += 1


def data_request_smartcitizen():
    """
    request the smartcitizen API and retrieve the API data
    :return:
    """
    connect()
    smartcitizen_request = requests.get('https://api.smartcitizen.me/v0/devices/world_map')
    smartcitizen_data = smartcitizen_request.json()
    count = 1
    saved = 0
    sensors_id = [12, 13, 15, 16]

    for device in smartcitizen_data:
        print(device['id'], "%d de %d" % (count, len(smartcitizen_data)))
        sc_device = SmartCitizenModel()
        sc_device.self_load(device['id'], device['latitude'], device['latitude'])
        all_sensor = 0

        for i in sensors_id:
            sensor_request = requests.get(
                'https://api.smartcitizen.me/v0/devices/'+str(device['id'])+'/readings?sensor_id='+str(i)+'&rollup=10m'
                '&from=2016-07-01'
            )
            sensor_data = sensor_request.json()
            if 'device_id' in sensor_data:
                if i == 12:
                    temp: SmartCitizenSensor = SmartCitizenSensor()
                    temp.self_load(sensor_data)
                    sc_device.temperature = temp
                elif i == 13:
                    hum: SmartCitizenSensor = SmartCitizenSensor()
                    hum.self_load(sensor_data)
                    sc_device.humidity = hum
                elif i == 15:
                    no2: SmartCitizenSensor = SmartCitizenSensor()
                    no2.self_load(sensor_data)
                    sc_device.no2 = no2
                elif i == 16:
                    co: SmartCitizenSensor = SmartCitizenSensor()
                    co.self_load(sensor_data)
                    sc_device.co = co

                if len(sensor_data['readings']) == 0:
                    all_sensor += 1
            else:
                all_sensor += 1
        if all_sensor != 0:
            print("here")
            count += 1
            continue

        if sc_device.self_validate():
            sc_device.save()
            saved += 1

        count += 1
        print("saved %d" % saved)


def data_request_purple_air():
    """
    request the purpleair API and retrieve the data
    :return:
    """
    connect()
    purple_air_api = requests.get('https://www.purpleair.com/json')
    purple_air_data = purple_air_api.json()
    count = 1

    for pa in purple_air_data['results']:
        print("%d de %d registros salvos" % (count, len(purple_air_data['results'])))
        purple_air_sensors_a = requests.get(
            'https://api.thingspeak.com/channels/'+pa['THINGSPEAK_PRIMARY_ID']+'/feeds.json?'
            'api_key='+pa['THINGSPEAK_PRIMARY_ID_READ_KEY']+'&start=2016-07-01'
        )
        purple_air_data_a = purple_air_sensors_a.json()

        purple_air_sensors_b = requests.get(
            'https://api.thingspeak.com/channels/' + pa['THINGSPEAK_SECONDARY_ID'] + '/feeds.json?'
            'api_key=' + pa['THINGSPEAK_SECONDARY_ID_READ_KEY'] + '&start=2016-07-01'
        )
        purple_air_data_b = purple_air_sensors_b.json()

        purple_air = PurpleAirModel()
        purple_air.self_load(
            pa['ID'], pa['ParentID'], pa['Lat'], pa['Lon'], purple_air_data_a['channel']['last_entry_id']
        )

        for reading in purple_air_data_a['feeds']:
            readings_a = PurpleAirReadings()
            readings_a.self_load(
                reading['entry_id'], reading['created_at'], temperature=reading['field6'], humidity=reading['field7'],
                pm2_5=reading['field8']
            )
            purple_air.readings_a.append(readings_a)

        for reading in purple_air_data_b['feeds']:
            readings_b = PurpleAirReadings()
            readings_b.self_load(
                reading['entry_id'], reading['created_at'], pm1=reading['field7'], pm10=reading['field8']
            )
            purple_air.readings_b.append(readings_b)

        if purple_air.self_validate():
            purple_air.save()
        else:
            print("obj not saved")
        count += 1


if __name__ == '__main__':
    data_request_purple_air()
