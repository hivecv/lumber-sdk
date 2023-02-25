import uuid

__defaults = {
    "api_url": "http://hub.hivecv.com/",
    "device_uuid": uuid.UUID(int=uuid.getnode()).hex,
}


def get(name):
    return __defaults.get(name)


def update(**kwargs):
    __defaults.update(**kwargs)

