import time

from lumber import config, hub

client = hub.LumberHubClient(
    credentials={"email": "test@test.com", "password": "zaq1@WSX"},
    # api_url="http://localhost:8000/"
)
client.start_heartbeat()

conf = config.DeviceConfig(schema='{"name": "string"}')
client.register(conf)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass


