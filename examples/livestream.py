import time
from lumber import config, hub
from lumber.tools import LumberLogHandler
import cv2
import depthai as dai

from lumber.tools.webrtc import LiveStream

client = hub.LumberHubClient(
    credentials={"email": "test@test.com", "password": "zaq1@WSX"},
    api_url="http://localhost:8000/"
)
# LumberLogHandler(client).enable()

conf = config.DeviceConfig(schema='{"name": "string", "debug": "number"}')
client.register(conf)

if not conf.is_valid():
    print("Waiting for config to be valid...")
    while not conf.is_valid():
        time.sleep(1)
    print(f"Received valid config! {conf._config}")

live = LiveStream(client)
live.start()

# pipeline = dai.Pipeline()
# xoutRgb = pipeline.create(dai.node.XLinkOut)
# xoutRgb.setStreamName("rgb")
#
# camRgb = pipeline.create(dai.node.ColorCamera)
# camRgb.setPreviewSize(300, 300)
# camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
# camRgb.preview.link(xoutRgb.input)

while True:
    time.sleep(1)

# with dai.Device(pipeline) as device:
#
#     qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
#
#     while True:
#         inRgb = qRgb.get()
        # frame = inRgb.getCvFrame()
        # cv2.imshow("rgb", frame)
        #
        # if cv2.waitKey(1) == ord('q'):
        #     break

