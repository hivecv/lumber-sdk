from lumber import config, hub

client = hub.LumberHubClient(
    credentials={"email": "test@test.com", "password": "zaq1@WSX"},
    # api_url="http://localhost:8000/"
)

conf = config.DeviceConfig(schema='{"name": "string"}')
response = conf.upload(client)
print(response.json())

