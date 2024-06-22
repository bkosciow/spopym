import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth


class Spotify:
    def __init__(self, cfg, lcd=None):
        self.spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
            open_browser=False,
            scope=cfg.get("spotify.scope"),
            client_id=cfg.get("spotify.client_id"),
            client_secret=cfg.get("spotify.client_secret"),
            redirect_uri=cfg.get("spotify.redirect_uri"),
        ))
        self.has_token = False if self.spotify.auth_manager.get_cached_token() is None else True
        self.lcd = lcd

    def authorize(self):
        self.lcd.show_authorize()
        # self.spotify.me()

    def menu_action(self, action):
        print(action)
        if action == 'Connect':
            self.authorize()

    def get_menu(self):
        if not self.has_token:
            return [
                {
                    'name': 'Connect',
                    'callback': self.menu_action
                }
            ]

        else:
            return []
