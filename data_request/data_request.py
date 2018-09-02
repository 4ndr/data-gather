import logging
import datetime
import threading
import sys
from datetime import timedelta
from json import JSONDecodeError

import requests
import sys
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


def data_request_purple_air(purple_air_data, limit_start: int, limit_end: int, logger):
    """
    request the purpleair API and retrieve the data
    :return:
    """
    connect()
    count = limit_start

    for pa in purple_air_data['results'][limit_start:limit_end]:
        logger.info("Salvando o sensor %d" % pa['ID'])
        logger.info("%d de %d" % (count, limit_end))
        try:
            purple_air_a = requests.get(
                'https://api.thingspeak.com/channels/'+pa['THINGSPEAK_PRIMARY_ID']+'/feeds.json?'
                'api_key='+pa['THINGSPEAK_PRIMARY_ID_READ_KEY']+'&start=2016-07-01'
            )

            purple_air_data_a = purple_air_a.json()

            purple_air_b = requests.get(
                'https://api.thingspeak.com/channels/' + pa['THINGSPEAK_SECONDARY_ID'] +
                '/feeds.json?api_key=' + pa['THINGSPEAK_SECONDARY_ID_READ_KEY'] + '&start=2016-07-01'
            )

            purple_air_data_b = purple_air_b.json()

            purple_air = PurpleAirModel()
            purple_air.self_load(
                pa['ID'], pa['ParentID'], pa['Lat'], pa['Lon'], purple_air_data_a['channel']['last_entry_id']
            )
            if purple_air.self_validate():
                purple_air.save()
                logger.info("Sensor %d salvo, salvando as leituras..." % pa['ID'])
            else:
                logger.error("Sensor %d nao foi salvo..." % pa['ID'])
                continue
            reading_a_count = 0
            reading_b_count = 0

            if 'error' in purple_air_data_a or 'error' in purple_air_data_b:
                continue

            if purple_air_data_a['channel']['last_entry_id'] and purple_air_data_a['channel']['last_entry_id'] > 8000:
                created_date = datetime.datetime.strptime(purple_air_data_a['channel']['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                end_date = datetime.datetime(2018, 7, 31)
                start_date = datetime.datetime(2016, 7, 1) if created_date < datetime.datetime(2016, 7, 1) else created_date
                date_actual = start_date + timedelta(hours=44, minutes=29)
                while date_actual < end_date:
                    date_formated_start = start_date.strftime("%Y-%m-%d %H:%M:%S")
                    date_formated = date_actual.strftime("%Y-%m-%d %H:%M:%S")
                    purple_air_sa = requests.get(
                        'https://api.thingspeak.com/channels/'+pa['THINGSPEAK_PRIMARY_ID'] + '/feeds.json?api_key='
                        + pa['THINGSPEAK_PRIMARY_ID_READ_KEY'] + '&start=' + date_formated_start.replace(" ", "%20")
                        + '&end='+date_formated.replace(" ", "%20")
                    )
                    purple_air_sb = requests.get(
                        'https://api.thingspeak.com/channels/' + pa['THINGSPEAK_SECONDARY_ID'] +
                        '/feeds.json?api_key=' + pa['THINGSPEAK_SECONDARY_ID_READ_KEY'] + '&start='
                        + date_formated_start.replace(" ", "%20") + '&end=' + date_formated.replace(" ", "%20")
                    )
                    
                    purple_air_sensor_a = purple_air_sa.json()
                    purple_air_sensor_b = purple_air_sb.json()

                    start_date = date_actual

                    if 'error' in purple_air_sensor_a or 'error' in purple_air_sensor_b:
                        date_actual = date_actual + timedelta(days=2)
                        continue

                    if not purple_air_sensor_a['feeds'] and not purple_air_sensor_b['feeds']:
                        start_date = start_date + timedelta(days=30)
                        date_actual = date_actual + timedelta(days=30)
                        continue

                    if 0 < len(purple_air_sensor_a['feeds']) < 2000:
                        date_actual = date_actual + timedelta(days=10)
                    elif 2000 < len(purple_air_sensor_a['feeds']) < 4000:
                         date_actual = date_actual + timedelta(days=6)
                    elif 4000 < len(purple_air_sensor_a['feeds']) < 7000:
                        date_actual = date_actual + timedelta(days=4)
                    else:
                        date_actual = date_actual + timedelta(days=2)

                    for reading in purple_air_sensor_a['feeds']:
                        readings_a = PurpleAirReadings()
                        readings_a.self_load(
                            pa['ID'], reading['entry_id'], reading['created_at'], temperature=reading['field6'],
                            humidity=reading['field7'], pm2_5=reading['field8']
                        )
                        if readings_a.self_validate():
                            readings_a.save()
                            reading_a_count += 1
                        else:
                            continue

                    for reading in purple_air_sensor_b['feeds']:
                        readings_b = PurpleAirReadings()
                        readings_b.self_load(
                            pa['ID'], reading['entry_id'], reading['created_at'], pm1=reading['field7'],
                            pm10=reading['field8']
                        )
                        if readings_b.self_validate():
                            readings_b.save()
                            reading_b_count += 1
                        else:
                            continue
                    logger.info(
                        "Para o sensor_id %d, [%d, %d] leituras foram salvas" % (
                            pa['ID'], reading_a_count, reading_b_count)
                    )
            else:
                for reading in purple_air_data_a['feeds']:
                    readings_a = PurpleAirReadings()
                    readings_a.self_load(
                        pa['ID'], reading['entry_id'], reading['created_at'], temperature=reading['field6'],
                        humidity=reading['field7'], pm2_5=reading['field8']
                    )
                    if readings_a.self_validate():
                        readings_a.save()
                        reading_a_count += 1
                    else:
                        continue

                for reading in purple_air_data_b['feeds']:
                    readings_b = PurpleAirReadings()
                    readings_b.self_load(
                        pa['ID'], reading['entry_id'], reading['created_at'], pm1=reading['field7'],
                        pm10=reading['field8']
                    )
                    if readings_b.self_validate():
                        readings_b.save()
                        reading_b_count += 1
                    else:
                        continue
                logger.info(
                    "Para o sensor_id %d, [%d, %d] leituras foram salvas" % (pa['ID'], reading_a_count, reading_b_count)
                )

            logger.info("%d de %d registros salvos" % (count, limit_end))
            count += 1
        except JSONDecodeError as e:
            logger.error("Erro no json: %s", e)
            logger.info("%d de %d registros não salvo" % (count, limit_end))
            count += 1
            continue
        except KeyError as e:
            logger.error("KeyError missing %s" % e)
            logger.info("%d de %d registros não salvo" % (count, limit_end))
            count += 1
            continue
        except:
            logger.info("%d de %d registros não salvo" % (count, limit_end))
            count += 1
            continue


def call_multi_thread(proccess_number):
    try:
        logger = configure_log()
        purple_air_api = requests.get('https://www.purpleair.com/json')
        purple_air_data = purple_air_api.json()
        if proccess_number == 1:
            thread = threading.Thread(target=data_request_purple_air, args=(purple_air_data, 4908, 4950, logger))
            thread.start()
        elif proccess_number == 2:
            thread5 = threading.Thread(target=data_request_purple_air, args=(purple_air_data, 4950, 5000, logger))
            thread5.start()

    except:
        print("Erro ao iniciar thread")


def configure_log():
    logger = logging.getLogger('purpleAirAPI')
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    hdlr_info = logging.FileHandler('log/info4.log')
    hdlr_info.setLevel(logging.INFO)
    hdlr_info.setFormatter(formatter)
    logger.addHandler(hdlr_info)

    hdlr_error = logging.FileHandler('log/error4.log')
    hdlr_error.setLevel(logging.ERROR)
    hdlr_error.setFormatter(formatter)
    logger.addHandler(hdlr_error)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger


if __name__ == '__main__':
    call_multi_thread()
