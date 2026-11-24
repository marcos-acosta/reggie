from screens import screen
from services import spotify
from ui import Column, Icon, Node, Picture

SPOTIFY_GREEN = "#1DB954"


@screen("spotify", refresh=10)
def album_cover() -> Node:
    playing = spotify.now_playing()
    if not playing or not playing.cover_url:
        return Column(
            Icon("spotify", color=SPOTIFY_GREEN), align="center", justify="center"
        )
    return Picture(spotify.fetch_cover(playing.cover_url))
