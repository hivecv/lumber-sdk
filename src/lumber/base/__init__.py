class HubEntity:
    client = None
    raw = {}

    def register_client(self, client):
        self.client = client

    def should_update(self, api_data):
        return self.raw != api_data

    def on_update(self, api_data):
        self.raw = api_data
