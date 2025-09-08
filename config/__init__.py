# config/__init__.py
import configparser
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "configs.ini")

if not os.path.exists(CONFIG_FILE):
    raise FileNotFoundError(f"Конфиг не найден: {CONFIG_FILE}")

config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# Экспорт настроек
AUTH_URL = config["AUTH"]["url"]
AUTH_TOKEN = config["AUTH"]["token"]

VERBOSE = config.getboolean("VERBOSE", "verbose")
TEST_INDEX = config.getint("TEST", "index")