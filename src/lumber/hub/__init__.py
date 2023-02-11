from lumber import settings
from urllib.parse import urljoin
import requests


class Routes:
    def __init__(self, api_url):
        self.token = urljoin(api_url, "token")
        self.users = urljoin(api_url, "users")
        self.users_devices = lambda user_id: urljoin(api_url, f"users/{user_id}/devices")
        self.devices = urljoin(api_url, "devices")
        self.me = urljoin(api_url, "users/me")
        self.me_devices = urljoin(api_url, "users/me/devices")


class LumberHubClient:
    api_url = None
    auth = None

    def __init__(self, credentials, api_url=settings.get('api_url')):
        self.api_url = api_url

        self._init_response = requests.options(self.api_url)
        if self._init_response.headers.get('server', '') != "uvicorn":
            raise ValueError("Provided API url - {} - is incorrect (not served by uvicorn). Possible network error!")

        self.routes = Routes(self.api_url)

        self._token_response = requests.post(self.routes.token, json=credentials)
        self._token_response.raise_for_status()
        self.auth = self._token_response.json()

        self._me_response = requests.get(self.routes.me, headers=self.auth_headers)
        self._me_response.raise_for_status()
        self.profile = self._me_response.json()

    @property
    def auth_headers(self):
        if self.auth is None:
            return {}
        return {"Authorization": f"{self.auth['token_type'].capitalize()} {self.auth['access_token']}"}

    def upload(self, item):
        if hasattr(item, 'send') and callable(item.send):
            item.send(self)

