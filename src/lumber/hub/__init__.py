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
        while getattr(instance, "_watcherRunning", False):
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
        self.login = urljoin(api_url, "login/")
        self.users = urljoin(api_url, "users/")
        self.me = urljoin(api_url, "users/me/")
        self.devices = urljoin(api_url, "devices/")
        self.device = urljoin(api_url, f"devices/{device_uuid}/")
        self.device_heartbeat = urljoin(api_url, f"devices/{device_uuid}/heartbeat/")
        self.device_logs = urljoin(api_url, f"devices/{device_uuid}/logs/")
        self.device_configs = urljoin(api_url, f"devices/{device_uuid}/configs/")
        self.device_config = lambda config_id: urljoin(api_url, f"devices/{device_uuid}/configs/{config_id}/")


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
            self.routes = Routes(self.api_url, self.device_uuid)

            self._login_response = requests.post(self.routes.login, json=credentials)
            self._login_response.raise_for_status()
            self.auth = self._login_response.json()

            self._me_response = requests.get(self.routes.me, headers=self.auth_headers)
            self._me_response.raise_for_status()

            response = requests.post(self.routes.devices, json={"device_uuid": self.device_uuid}, headers=self.auth_headers)
            response.raise_for_status()
        except ConnectionError:
            raise ValueError("Provided API url - {} - is incorrect (not served by uvicorn). Possible network error!".format(self.api_url))

    @property
    def auth_headers(self):
        if self.auth is None:
            return {}
        return {"Authorization": f"{self.auth['token_type'].capitalize()} {self.auth['access_token']}"}

    def register(self, item: HubEntity):
        item.register_client(self)

        if isinstance(item, DeviceConfig):
            configs_response = requests.get(self.routes.device_configs, headers=self.auth_headers)
            configs_response.raise_for_status()
            for config in configs_response.json():
                if item.is_matching(config):
                    return WatchedItem(self.routes.device_config(config["id"]), item)

            response = requests.post(self.routes.device_configs, json=dict(item), headers=self.auth_headers)
            response.raise_for_status()
            data = response.json()
            return WatchedItem(self.routes.device_config(data["id"]), item)

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



