import time
import traceback
from threading import Thread

from lumber import settings
from urllib.parse import urljoin
import requests

from lumber.base import HubEntity
from lumber.config import DeviceConfig


class WatchedItem:
    _watcherRunning = False
    _watcher = None

    def __init__(self, url: str, item: HubEntity):
        self._url = url
        if item.client is None:
            raise ValueError("Item not registered in HubClient instance!")
        self._item = item

    def fetch_api(self):
        devices_response = requests.get(self._url, headers=self._item.client.auth_headers)
        devices_response.raise_for_status()
        return devices_response.json()

    def update(self, api_data: dict = None):
        if api_data is None:
            api_data = self.fetch_api()
        if self._item.should_update(api_data):
            self._item.on_update(api_data)

    @staticmethod
    def _watcher_thread(instance):
        while instance._watcherRunning:
            try:
                instance.update()
            except:
                pass
            time.sleep(5)

    def watch(self):
        self._watcherRunning = True
        self._watcher = Thread(target=WatchedItem._watcher_thread, args=(self, ))
        self._watcher.daemon = True
        self._watcher.start()

    def unwatch(self):
        self._watcherRunning = False
        self._watcher.join()


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


class LumberHubClient:
    api_url = None
    auth = None

    _heartbeat = None
    _heartbeat_running = False

    _watched = []

    def __init__(self, credentials, api_url=settings.get('api_url'), device_uuid=settings.get('device_uuid')):
        self.api_url = api_url
        self.device_uuid = device_uuid

        try:
            self._init_response = requests.options(self.api_url)
        except ConnectionError:
            raise ValueError("Provided API url - {} - is incorrect (not served by uvicorn). Possible network error!".format(self.api_url))

        self.routes = Routes(self.api_url, self.device_uuid)

        self._token_response = requests.post(self.routes.token, json=credentials)
        self._token_response.raise_for_status()
        self.auth = self._token_response.json()

        self._me_response = requests.get(self.routes.me, headers=self.auth_headers)
        self._me_response.raise_for_status()

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
                    return WatchedItem(self.routes.me_device(device["id"]), item)
            response = requests.post(self.routes.me_devices, json={**dict(item), "device_uuid": self.device_uuid}, headers=self.auth_headers)
            response.raise_for_status()
            item.on_update(response.json())
            return WatchedItem(self.routes.me_device(item.raw["id"]), item)

    def _heartbeat_thread(self):
        while self._heartbeat_running:
            try:
                requests.patch(self.routes.device_heartbeat, headers=self.auth_headers)
            except:
                pass

            time.sleep(1)

    def start_heartbeat(self):
        self._heartbeat_running = True
        self._heartbeat = Thread(target=self._heartbeat_thread)
        self._heartbeat.daemon = True
        self._heartbeat.start()

    def stop_heartbeat(self):
        self._heartbeat_running = False
        self._heartbeat.join()



