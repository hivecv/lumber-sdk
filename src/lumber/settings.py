import uuid

__defaults = {
    "api_url": "https://hub.hivecv.com/api/",
    "device_uuid": uuid.UUID(int=uuid.getnode()).hex,
}


def get(name):
    return __defaults.get(name)


def update(**kwargs):
    __defaults.update(**kwargs)

