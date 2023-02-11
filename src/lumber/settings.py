__defaults = {
    "api_url": "http://hub.hivecv.com/",
}


def get(name):
    return __defaults.get(name)


def update(**kwargs):
    __defaults.update(**kwargs)

