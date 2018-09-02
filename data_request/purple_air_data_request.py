from json import JSONDecodeError

import requests


class PurpleAirDataRequest(object):
    """
    Makes data request through api
    """
    def __init__(self, url):
        self.url = url
        self.url_a = str()
        self.url_b = str()

    def get_all_sensors(self):
        purple_air_api = requests.get(self.url)
        purple_air_data = purple_air_api.json()
        return purple_air_data['results']

    def get_sensor_a(self):
        try:
            purple_air_sensors_a = requests.get(self.url_a)
            purple_air_data_a = purple_air_sensors_a.json()
            return purple_air_data_a

        except JSONDecodeError as e:
            print(e)
        except KeyError as e:
            print("KeyError missing %s" % e)

    def get_sensor_b(self):
        try:
            purple_air_sensors_a = requests.get(self.url_a)
            purple_air_data_a = purple_air_sensors_a.json()
            return purple_air_data_a

        except JSONDecodeError as e:
            print(e)
        except KeyError as e:
            print("KeyError missing %s" % e)

    def more_than_8000(self):
        pass
