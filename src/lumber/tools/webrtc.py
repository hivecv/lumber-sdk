import time
from threading import Thread

from lumber.hub import LumberHubClient


class LiveStream:
    request_action = None

    _t = None
    _running = False
    _connected = False

    def __init__(self, client: LumberHubClient):
        self.client = client

    def _thread(self):
        while self._running:
            print(self.client._actions._actions)
            time.sleep(1)

    def start(self):
        self._running = True
        self._t = Thread(target=self._thread)
        self._t.daemon = True
        self._t.start()

    def stop(self):
        self._running = False
        self._t.join()

