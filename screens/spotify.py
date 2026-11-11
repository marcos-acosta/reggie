from screens import screen
from services import spotify
from ui import Box, Node, Picture


@screen("spotify", refresh=10)
def album_cover() -> Node:
    playing = spotify.now_playing()
    if not playing or not playing.cover_url:
        return Box()
    return Picture(spotify.fetch_cover(playing.cover_url))
