import traceback

from lumber import settings
from urllib.parse import urljoin
import requests
from requests.exceptions import ConnectionError
from lumber.base import HubEntity
from lumber.config import DeviceConfig
from lumber.hub.actions import HubActions
from lumber.hub.heartbeat import Heartbeat


class WatchedItem(Heartbeat):
    _watcherRunning = False
    _watcher = None

    def __init__(self, url: str, item: HubEntity, frequency=0.2):
        self._url = url
        if item.client is None:
            raise ValueError("Item not registered in HubClient instance!")
        self._item = item
        super().__init__(self.update, frequency=frequency)

    def fetch_api(self):
        devices_response = requests.get(self._url, headers=self._item.client.auth_headers)
        devices_response.raise_for_status()
        return devices_response.json()

    def update(self, api_data: dict = None):
        try:
            if api_data is None:
                api_data = self.fetch_api()
            if self._item.should_update(api_data):
                self._item.on_update(api_data)
        except Exception:
            pass
            # traceback.print_exc()


class Routes:
    def __init__(self, api_url, device_uuid):
        self.token = urljoin(api_url, "token/")
        self.users = urljoin(api_url, "users/")
        self.devices = urljoin(api_url, "devices/")
        self.me = urljoin(api_url, "users/me/")
        self.me_devices = urljoin(api_url, "users/me/devices/")
        self.me_device = lambda device_id: urljoin(api_url, f"users/me/devices/{device_id}/")
        self.device_heartbeat = urljoin(api_url, f"users/me/devices/{device_uuid}/heartbeat/")
        self.device_logs = urljoin(api_url, f"users/me/devices/{device_uuid}/logs/")
        self.device_actions = urljoin(api_url, f"users/me/devices/{device_uuid}/actions/")


class LumberHubClient:
    api_url = None
    auth = None

    _heartbeat = None
    _actions = None

    def __init__(self, credentials, api_url=settings.get('api_url'), device_uuid=settings.get('device_uuid')):
        self.api_url = api_url
        self.device_uuid = device_uuid

        try:
            self._init_response = requests.options(self.api_url)
        except ConnectionError:
            raise ValueError("Provided API url - {} - is incorrect, possible network error!".format(self.api_url)) from None  # to clear the callstack

        self.routes = Routes(self.api_url, self.device_uuid)

        self._token_response = requests.post(self.routes.token, json=credentials)
        self._token_response.raise_for_status()
        self.auth = self._token_response.json()

        self._me_response = requests.get(self.routes.me, headers=self.auth_headers)
        self._me_response.raise_for_status()

        self._heartbeat = Heartbeat(
            on_beat=lambda: requests.patch(self.routes.device_heartbeat, headers=self.auth_headers)
        )
        self._heartbeat.start()

        self._actions = HubActions()
        self._actions.register_client(self)
        WatchedItem(self.routes.device_actions, self._actions, frequency=1).start()

    @property
    def auth_headers(self):
        if self.auth is None:
            return {}
        return {"Authorization": f"{self.auth['token_type'].capitalize()} {self.auth['access_token']}"}

    def register(self, item: HubEntity):
        item.register_client(self)

        if isinstance(item, DeviceConfig):
            devices_response = requests.get(self.routes.me_devices, headers=self.auth_headers)
            devices_response.raise_for_status()
            for device in devices_response.json():
                if device["device_uuid"] == self.device_uuid:
                    item._config = device.get("config", item._config)
                    response = requests.put(self.routes.me_device(device["id"]), json={**device, **dict(item)}, headers=self.auth_headers)
                    response.raise_for_status()
                    item.on_update(response.json())
                    WatchedItem(self.routes.me_device(device["id"]), item).start()
            response = requests.post(self.routes.me_devices, json={**dict(item), "device_uuid": self.device_uuid}, headers=self.auth_headers)
            response.raise_for_status()
            item.on_update(response.json())
            WatchedItem(self.routes.me_device(item.raw["id"]), item).start()

    def send_action(self, payload):
        pass


