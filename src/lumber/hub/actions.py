import json

from lumber.base import HubEntity


class HubActions(HubEntity):
    _actions = []

    def __iter__(self):
        yield 'actions', self._actions

    def should_update(self, api_data):
        if not api_data:
            return False
        return len(self._actions) != len(api_data)

    def on_update(self, api_data):
        super().on_update(api_data)
        self._actions = api_data
