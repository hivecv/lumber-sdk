import requests

from lumber.hub import LumberHubClient


class DeviceConfig:
    _schema = ""

    def __init__(self, schema):
        self._schema = schema

    def __iter__(self):
        yield 'config_schema', self._schema

    def upload(self, hub: LumberHubClient):
        response = requests.post(hub.routes.users_devices(hub.profile['id']), json=dict(self))
        response.raise_for_status()
        return response
