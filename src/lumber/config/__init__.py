import uuid


class DeviceConfig:
    _schema = ""
    _config = None

    def __init__(self, schema):
        self._schema = schema

    def __iter__(self):
        yield 'config_schema', self._schema
