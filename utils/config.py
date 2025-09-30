import dataclasses
import json
import pathlib

root = pathlib.Path(__file__).resolve().parent.parent
config_path = root / 'assets/secure' / 'config.json'


@dataclasses.dataclass
class Settings:
    tg_bot_token: str
    db_file: pathlib.Path
    log_file: pathlib.Path
    template_dir: pathlib.Path
    redis_url: str
    cache_lifetime: int
    answer_timeout: int

    def __post_init__(self):
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            setattr(self, field.name, field.type(value))
            if field.name.endswith("_file") or field.name.endswith("_dir"):
                setattr(self, field.name, root / value)


with open(config_path) as file:
    params = json.load(file)
    settings = Settings(**params)
