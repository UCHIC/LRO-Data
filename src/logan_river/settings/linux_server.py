from logan_river.settings.base import *

DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
if "host" in config:
    ALLOWED_HOSTS.append(config["host"])
if "host_alt" in config:
    ALLOWED_HOSTS.append(config["host_alt"])

STATIC_ROOT = config["static_root"]
SITE_ROOT = config["site_root"]
STATIC_URL = config["static_url"]
SITE_URL = ''
