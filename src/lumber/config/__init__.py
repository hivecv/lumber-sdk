from lumber.base import HubEntity
from jsonschema import validate, ValidationError


class DeviceConfig(HubEntity):
    _schema = ""
    _config = None

    def __init__(self, schema):
        self._schema = schema

    def __iter__(self):
        yield 'config_schema', self._schema

    def is_matching(self, other):
        if isinstance(other, dict):
            return 'config_schema' in other and self._schema == other['config_schema']
        return False

    def should_update(self, api_data):
        if not super().should_update(api_data) or 'config' not in api_data:
            return False
        return self._config != api_data['config']

    def on_update(self, api_data):
        super().on_update(api_data)
        self._config = api_data['config']

    def get_validation_schema(self):
        return {
            "type": "object",
            "properties": {
                field_name: {"type": field_type}
                for field_name, field_type in self._schema.items()
            },
        }

    def is_valid(self, strict=True):
        if not self._schema or not self._config:
            return False
        try:
            schema = self.get_validation_schema()
            if strict:
                schema['required'] = list(schema['properties'].keys())
            validate(self._config, schema)
            return True
        except ValidationError:
            return False
