import io
import os
from dataclasses import dataclass
from functools import cache, lru_cache
from pathlib import Path

import requests
import spotipy
from dotenv import load_dotenv
from PIL import Image
from spotipy.cache_handler import CacheFileHandler
from spotipy.oauth2 import SpotifyOAuth

ROOT = Path(__file__).resolve().parent.parent
TOKEN_CACHE = ROOT / ".spotify-cache"
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE = "user-read-currently-playing"
TIMEOUT = 5


@dataclass(frozen=True)
class NowPlaying:
    title: str
    artists: tuple[str, ...]
    cover_url: str | None


@cache
def client() -> spotipy.Spotify:
    load_dotenv(ROOT / ".env")
    auth = SpotifyOAuth(
        client_id=os.environ["SPOTIFY_CLIENT_ID"],
        client_secret=os.environ["SPOTIFY_CLIENT_SECRET"],
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_handler=CacheFileHandler(cache_path=str(TOKEN_CACHE)),
    )
    return spotipy.Spotify(auth_manager=auth, requests_timeout=TIMEOUT)


def now_playing() -> NowPlaying | None:
    current = client().current_user_playing_track()
    item = current and current.get("item")
    if not item:
        return None
    images = item.get("album", {}).get("images") or item.get("images") or []
    smallest = min(images, key=lambda image: image.get("width") or 0, default=None)
    return NowPlaying(
        title=item["name"],
        artists=tuple(artist["name"] for artist in item.get("artists", [])),
        cover_url=smallest and smallest["url"],
    )


@lru_cache(maxsize=16)
def fetch_cover(url: str) -> Image.Image:
    response = requests.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    return Image.open(io.BytesIO(response.content)).convert("RGB")


if __name__ == "__main__":
    playing = now_playing()
    print(f"{playing.title} — {', '.join(playing.artists)}" if playing else "Nothing playing")
