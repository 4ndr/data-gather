import datetime
from typing import List

from mongoengine import Document, StringField, IntField, DateTimeField, GeoPointField, ValidationError, \
    EmbeddedDocument, EmbeddedDocumentListField, FloatField, EmbeddedDocumentField


class SafeCastModel(Document):
    """
    SafeCastModel for PM2.5 and PM10
    """
    id_m = IntField(required=True)
    user_id = IntField(required=True)
    value = IntField(required=True)
    unit = StringField()
    location_name = StringField()
    device_id = IntField()
    original_id = IntField()
    measurement_import_id = StringField()
    captured_at = DateTimeField()
    height = IntField()
    devicetype_id = StringField()
    sensor_id = IntField()
    station_id = StringField()
    channel_id = StringField()
    location = GeoPointField()
    meta = {'collection': 'SafeCast'}

    def self_load(self, data: dict):
        """
        load this object data
        :return: self
        """
        self.id_m = data['id']
        self.user_id = data['user_id']
        self.value = data['value']
        self.unit = data['unit']
        self.location_name = data['location_name']
        self.device_id = data['device_id']
        self.original_id = data['original_id']
        self.measurement_import_id = data['measurement_import_id']
        self.captured_at = datetime.datetime.strptime(data['captured_at'], "%Y-%m-%dT%H:%M:%S.000Z")
        self.height = data['height']
        self.devicetype_id = data['devicetype_id']
        self.sensor_id = data['sensor_id']
        self.station_id = data['station_id']
        self.channel_id = data['channel_id']
        self.location = [data['latitude'], data['longitude']]

        return self

    def self_validate(self):
        """
        Verify is the model is valid to save on mongo
        :return: self
        """
        try:
            super(SafeCastModel, self).validate()
            return True
        except ValidationError as e:
            print("Falha na validação do model %s" % e)
            return False


class SCReading(EmbeddedDocument):
    """
    Embedded document to represent the devices reading
    """
    date = DateTimeField()
    value = FloatField()

    def self_load(self, data: list):
        """
        load this object data
        :return: self
        """
        self.date = datetime.datetime.strptime(data[0], "%Y-%m-%dT%H:%M:%SZ")
        self.value = data[1]

        return self

    def self_validate(self):
        """
        Verify is the model is valid to save on mongo
        :return: self
        """
        try:
            super(SCReading, self).validate()
            return True
        except ValidationError as e:
            print("Falha na validação do model %s" % e)
            return False


class SmartCitizenSensor(EmbeddedDocument):
    """

    """
    sensor_key = StringField()
    sensor_id = IntField()
    component_id = IntField()
    rollup = StringField()
    function = StringField()
    date_from = DateTimeField()
    date_to = DateTimeField()
    sample_size = IntField()
    readings: List[SCReading] = EmbeddedDocumentListField(SCReading)

    def self_load(self, data: dict):
        """
        load this object data
        :return: self
        """
        self.sensor_key = data['sensor_key']
        self.sensor_id = data['sensor_id']
        self.component_id = data['component_id']
        self.rollup = data['rollup']
        self.function = data['function']
        self.date_from = datetime.datetime.strptime(data['from'], "%Y-%m-%dT%H:%M:%SZ")
        self.date_to = datetime.datetime.strptime(data['to'], "%Y-%m-%dT%H:%M:%SZ")
        self.sample_size = data['sample_size']
        self.readings: List[SCReading] = list()
        for reading in data['readings']:
            r = SCReading()
            r.self_load(reading)
            self.readings.append(r)

        return self

    def self_validate(self):
        """
        Verify if the model is valid to save on mongo
        :return: self
        """
        try:
            super(SmartCitizenSensor, self).validate()
            return True
        except ValidationError as e:
            print("Falha na validação do model %s" % e)
            return False


class SmartCitizenModel(Document):
    """
    SmartCitizenModel for NO2, CO, Temperature and humidity
    """
    device_id = IntField()
    location = GeoPointField()
    temperature: SmartCitizenSensor = EmbeddedDocumentField(SmartCitizenSensor, default=SmartCitizenSensor())
    humidity: SmartCitizenSensor = EmbeddedDocumentField(SmartCitizenSensor, default=SmartCitizenSensor())
    no2: SmartCitizenSensor = EmbeddedDocumentField(SmartCitizenSensor, default=SmartCitizenSensor())
    co: SmartCitizenSensor = EmbeddedDocumentField(SmartCitizenSensor, default=SmartCitizenSensor())

    meta = {'collection': 'SmartCitizen_2'}

    def self_load(self, device_id: str, latitude, longitude):
        """
        load this object data
        :return: self
        """
        self.device_id = device_id
        self.location = [latitude, longitude]

        return self

    def self_validate(self):
        """
        Verify is the model is valid to save on mongo
        :return: self
        """
        try:
            super(SmartCitizenModel, self).validate()
            return True
        except ValidationError as e:
            print("Falha na validação do model %s" % e)
            return False


class PurpleAirReadings(EmbeddedDocument):
    """
    PurpleAirModel for PM2.5, Temperature and humidity
    """
    entry_id = IntField()
    created_at = DateTimeField()
    temperature = StringField()
    humidity = StringField()
    pm2_5 = StringField()
    pm1 = StringField()
    pm10 = StringField()

    def self_load(self, entry_id, created_at, temperature=None, humidity=None, pm2_5=None, pm1=None, pm10=None):
        """
        load this object data
        :return: self
        """
        self.entry_id = entry_id
        self.created_at = datetime.datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
        if temperature:
            self.temperature = temperature
        if humidity:
            self.humidity = humidity
        if pm2_5:
            self.pm2_5 = pm2_5
        if pm1:
            self.pm1 = pm1
        if pm10:
            self.pm10 = pm10

        return self

    def self_validate(self):
        """
        Verify is the model is valid to save on mongo
        :return: self
        """
        try:
            super(PurpleAirReadings, self).validate()
            return True
        except ValidationError as e:
            print("Falha na validação do model %s" % e)
            return False


class PurpleAirModel(Document):
    """
    PurpleAirModel for PM2.5, Temperature and humidity
    """
    device_id = IntField()
    parent_id = IntField()
    location: List[int] = GeoPointField()
    last_entry_id = IntField()
    readings_a: List[PurpleAirReadings] = EmbeddedDocumentListField(PurpleAirReadings, default=[])
    readings_b: List[PurpleAirReadings] = EmbeddedDocumentListField(PurpleAirReadings, default=[])

    meta = {'collection': 'PurpleAir_2'}

    def self_load(self, device_id: str, parent_id, latitude, longitude, last_entry_id):
        """
        load this object data
        :return: self
        """
        self.device_id = device_id
        self.parent_id = parent_id
        self.location = [latitude, longitude]
        self.last_entry_id = last_entry_id

        return self

    def self_validate(self):
        """
        Verify is the model is valid to save on mongo
        :return: self
        """
        try:
            super(PurpleAirModel, self).validate()
            return True
        except ValidationError as e:
            print("Falha na validação do model %s" % e)
            return False
