import time
from threading import Thread


class Heartbeat:
    _t = None
    _running = False

    def __init__(self, on_beat, frequency=1):
        self.frequency = frequency
        self.on_beat = on_beat

    def _thread(self):
        while self._running:
            try:
                self.on_beat()
            except:
                pass

            time.sleep(1/self.frequency)

    def start(self):
        self._running = True
        self._t = Thread(target=self._thread)
        self._t.daemon = True
        self._t.start()

    def stop(self):
        self._running = False
        self._t.join()
