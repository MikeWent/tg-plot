import json
import random
import string
from dataclasses import dataclass
from os import getenv
from threading import Lock

SETTINGS_FILE = getenv("SETTINGS_FILE", "data/settings.json")


def random_string(length: int) -> str:
    return "".join(
        [random.choice(string.ascii_letters + string.digits) for _ in range(length)]
    )


@dataclass(init=False)
class Settings:
    def default(self):
        self.app_name: str = "tg-plot"
        self.app_secret_key: str = random_string(32)
        self.app_data_dir: str = "./data/"

        self.admin_password_hash: str = ""
        self.view_password_required: bool = False

        self.telegram_api_id: int = 0
        self.telegram_api_hash: str = ""
        self.telegram_channel_id: int = -0

    def __init__(self, filename: str) -> None:
        self._filename = filename
        self._lock = Lock()
        self.default()
        try:
            self.load()
        except FileNotFoundError:
            # create a file
            self.save()

    def update(self, new_settings: dict):
        for k, v in new_settings.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def save(self):
        with self._lock:
            with open(self._filename, "w") as f:
                saved = self.__dict__.copy()
                saved.pop("_filename", None)
                saved.pop("_lock", None)
                json.dump(saved, f, indent=2)

    def load(self):
        with self._lock:
            with open(self._filename, "r") as f:
                loaded: dict = json.load(f)
                loaded.pop("_filename", None)
                loaded.pop("_lock", None)
                self.__dict__.update(loaded)


settings = Settings(SETTINGS_FILE)
