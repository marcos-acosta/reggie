import tomllib
from dataclasses import dataclass
from functools import cache
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.toml"


@dataclass(frozen=True)
class DisplayConfig:
    brightness: int


@dataclass(frozen=True)
class ScreenConfig:
    id: str
    name: str


@dataclass(frozen=True)
class RemoteConfig:
    port: int
    address: int
    buttons: dict[int, str]


@cache
def _load() -> dict:
    with CONFIG_PATH.open("rb") as file:
        return tomllib.load(file)


def display_config(kind: str) -> DisplayConfig:
    return DisplayConfig(**_load()["display"][kind])


def screen_configs() -> list[ScreenConfig]:
    return [ScreenConfig(**entry) for entry in _load().get("screens", [])]


def remote_config() -> RemoteConfig:
    remote = _load()["remote"]
    buttons = {int(code): action for code, action in remote["buttons"].items()}
    return RemoteConfig(port=remote["port"], address=remote["address"], buttons=buttons)
