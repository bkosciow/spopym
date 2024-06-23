import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from service.menu import MenuItem


class Spotify:
    def __init__(self, config):
        self.config = config
        self.spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
            open_browser=False,
            scope=config.get("spotify.scope"),
            client_id=config.get("spotify.client_id"),
            client_secret=config.get("spotify.client_secret"),
            redirect_uri=config.get("spotify.redirect_uri"),
        ))
        self.config.set_param("spotify_token", False if self.spotify.auth_manager.get_cached_token() is None else True)
        self.auth_callback = None

    def get_menu(self):
        if not self.config.get_param("spotify_token"):
            return [
                MenuItem('Connect', action_name='spotify.connect', callback=self.auth_callback)
            ]
        else:
            return []
