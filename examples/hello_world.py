import time
from lumber import config, hub
from lumber.tools import LumberLogHandler

client = hub.LumberHubClient(
    credentials={"email": "test@test.com", "password": "zaq1@WSX"},
    # api_url="http://localhost:8000/"
)
client.start_heartbeat()
LumberLogHandler(client).enable()

conf = config.DeviceConfig(schema='{"name": "string", "debug": "number"}')
watcher = client.register(conf)
watcher.watch()
print("Registered config!")

try:
    while True:
        print(f"Config valid: {conf.is_valid()}, schema: {conf._schema}, data: {conf._config}")
        time.sleep(2)
except KeyboardInterrupt:
    pass


