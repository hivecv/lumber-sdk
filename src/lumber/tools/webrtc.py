import asyncio
import time
import uuid
from datetime import datetime
from threading import Thread
from aiortc.sdp import candidate_from_sdp
from aiortc import RTCSessionDescription, RTCPeerConnection
from lumber.hub import LumberHubClient


class LiveStream:
    _latest_action_ts = None

    _t = None
    _running = False
    _connected = False

    __offer = None
    __pc = None

    def __init__(self, client: LumberHubClient):
        self.client = client

    async def __async_thread(self):
        while self._running:
            for action in filter(lambda item: item["name"] == "LIVESTREAM_CLIENT", self.client._actions._actions):
                ts = datetime.fromisoformat(action['created']).replace(tzinfo=None)
                if self._latest_action_ts is None or ts > self._latest_action_ts:
                    await self._parse_action(action)
                    self._latest_action_ts = ts

    def _thread(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self.__async_thread())
        finally:
            loop.close()


            # {'name': 'LIVESTREAM_START', 'payload': {'sdp': ''}, 'id': 9, 'created': '2023-03-16T11:58:35.337382+00:00'}
            # candidate: {candidate: 'candidate:2143639293 1 udp 2113937151 62f4dc46-7e3…typ host generation 0 ufrag hPoq network-cost 999', sdpMLineIndex: 0, sdpMid: '0'}
            # type: "candidate"
            # sdp:"v=0\r\no=- 3049925003064880256 2 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\na=group:BUNDLE 0\r\na=extmap-allow-mixed\r\na=msid-semantic: WMS\r\nm=application 9 UDP/DTLS/SCTP webrtc-datachannel\r\nc=IN IP4 0.0.0.0\r\na=ice-ufrag:1Tj3\r\na=ice-pwd:M4mkfv3loM3NDqKdhvlB/TMG\r\na=ice-options:trickle\r\na=fingerprint:sha-256 AE:DA:76:7A:8A:59:5C:9F:3F:7A:20:07:CC:49:BD:AB:F5:D6:EF:54:73:FD:D6:D0:CA:16:F9:18:82:89:07:DE\r\na=setup:active\r\na=mid:0\r\na=sctp-port:5000\r\na=max-message-size:262144\r\n"
            # type:"answer"
            time.sleep(1)

    async def _parse_action(self, action):
        payload = action['payload']
        if payload['type'] == "candidate":
            print("Received a candidate: ", payload['candidate'])
            if self.__pc:
                candidate = candidate_from_sdp(payload['candidate']['candidate'])
                candidate.sdpMid = payload['candidate']['sdpMid']
                candidate.sdpMLineIndex = payload['candidate']['sdpMLineIndex']
                await self.__pc.addIceCandidate(candidate)
                print("Candidate added!")
            else:
                print("No active peer connection")
        elif payload['type'] == "offer":
            print("Received an offer: ", payload['sdp'])
            self.__pc = RTCPeerConnection()
            self.__offer = RTCSessionDescription(sdp=payload['sdp'], type=payload['type'])
            await self.__pc.setRemoteDescription(self.__offer)
            await self.__pc.setLocalDescription(await self.__pc.createAnswer())
            self.client.send_action({
                "name": "LIVESTREAM_SERVER",
                "payload": {
                    "type": self.__pc.localDescription.type,
                    "sdp": self.__pc.localDescription.sdp,
                }
            })
            print("Response sent!")
        else:
            print("Unknown action: ", action)

    def start(self):
        self._running = True
        self._t = Thread(target=self._thread)
        self._t.daemon = True
        self._t.start()

    def stop(self):
        self._running = False
        self._t.join()

