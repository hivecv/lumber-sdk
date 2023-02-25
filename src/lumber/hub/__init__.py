import time
import traceback
from threading import Thread

from lumber import settings
from urllib.parse import urljoin
import requests

from lumber.config import DeviceConfig


class Routes:
    def __init__(self, api_url):
        self.token = urljoin(api_url, "token/")
        self.users = urljoin(api_url, "users/")
        self.devices = urljoin(api_url, "devices/")
        self.me = urljoin(api_url, "users/me/")
        self.me_devices = urljoin(api_url, "users/me/devices/")
        self.me_device = lambda device_id: urljoin(api_url, f"users/me/devices/{device_id}/")
        self.me_device_heartbeat = lambda device_id: urljoin(api_url, f"users/me/devices/{device_id}/heartbeat/")


class LumberHubClient:
    api_url = None
    auth = None

    _heartbeat = None
    _heartbeat_running = False

    def __init__(self, credentials, api_url=settings.get('api_url'), device_uuid=settings.get('device_uuid')):
        self.api_url = api_url

        self._init_response = requests.options(self.api_url)
        self._init_response.raise_for_status()

        self.routes = Routes(self.api_url)

        self._token_response = requests.post(self.routes.token, json=credentials)
        self._token_response.raise_for_status()
        self.auth = self._token_response.json()

        self._me_response = requests.get(self.routes.me, headers=self.auth_headers)
        self._me_response.raise_for_status()

        self.device_uuid = device_uuid

    @property
    def auth_headers(self):
        if self.auth is None:
            return {}
        return {"Authorization": f"{self.auth['token_type'].capitalize()} {self.auth['access_token']}"}

    def register(self, item):
        if isinstance(item, DeviceConfig):
            devices_response = requests.get(self.routes.me_devices, headers=self.auth_headers)
            devices_response.raise_for_status()
            for device in devices_response.json():
                if device["device_uuid"] == self.device_uuid:
                    item._config = device.get("config", item._config)
                    print({**dict(item), "device_uuid": self.device_uuid})
                    response = requests.put(self.routes.me_device(device["id"]), json={**device, **dict(item)}, headers=self.auth_headers)
                    response.raise_for_status()
                    return item
            response = requests.post(self.routes.me_devices, json={**dict(item), "device_uuid": self.device_uuid})
            response.raise_for_status()
            return item

    def _heartbeat_thread(self):
        while self._heartbeat_running:
            try:
                requests.patch(self.routes.me_device_heartbeat(self.device_uuid), headers=self.auth_headers)
            except:
                traceback.print_exc()

            time.sleep(1)

    def start_heartbeat(self):
        self._heartbeat_running = True
        self._heartbeat = Thread(target=self._heartbeat_thread)
        self._heartbeat.daemon = True
        self._heartbeat.start()

    def stop_heartbeat(self):
        self._heartbeat_running = False
        self._heartbeat.join()



