from collections.abc import Iterable
from dataclasses import dataclass

from config import ScreenConfig, screen_configs


@dataclass(frozen=True)
class Entry:
    number: int
    id: str
    name: str

    @property
    def label(self) -> str:
        return f"{self.number} {self.name}"


@dataclass(frozen=True)
class Lineup:
    entries: list[Entry]
    unknown_ids: list[str]

    def find(self, key: str) -> Entry | None:
        """Looks a screen up by number, display name or registered id."""
        return next((entry for entry in self.entries if key in (str(entry.number), entry.name, entry.id)), None)

    def step(self, screen_id: str, offset: int) -> Entry:
        ids = [entry.id for entry in self.entries]
        index = ids.index(screen_id) if screen_id in ids else -1
        return self.entries[(index + offset) % len(self.entries)]


def build_lineup(registered: Iterable[str]) -> Lineup:
    registered = set(registered)
    configured = [config for config in screen_configs() if config.id in registered]
    listed = {config.id for config in configured}
    extras = [ScreenConfig(id=screen_id, name=screen_id) for screen_id in sorted(registered - listed)]
    entries = [Entry(number, config.id, config.name) for number, config in enumerate(configured + extras, 1)]
    unknown = [config.id for config in screen_configs() if config.id not in registered]
    return Lineup(entries, unknown)
