import tomllib
from dataclasses import dataclass
from functools import cache
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.toml"


@dataclass(frozen=True)
class DisplayConfig:
    brightness: int


@cache
def _load() -> dict:
    with CONFIG_PATH.open("rb") as file:
        return tomllib.load(file)


def display_config(kind: str) -> DisplayConfig:
    return DisplayConfig(**_load()["display"][kind])
