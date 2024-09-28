import spotipy
from spotipy.oauth2 import SpotifyOAuth
from service.track_data import TrackData
from service.menu import MenuItem
import threading
import time


class Spotify(threading.Thread):
    def __init__(self, config, fetch_tick=2):
        super().__init__()

        self.config = config
        self.fetch_tick = fetch_tick
        self.spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
            open_browser=False,
            scope=config.get("spotify.scope"),
            client_id=config.get("spotify.client_id"),
            client_secret=config.get("spotify.client_secret"),
            redirect_uri=config.get("spotify.redirect_uri"),
        ))
        self.config.set_param("spotify_token", False if self.spotify.auth_manager.get_cached_token() is None else True)
        self.auth_callback = None
        self.menu_callback = None
        self.data = TrackData()
        self.work = True

        if self.config.get_param('spotify_token'):
            self.get_devices()

    def get_menu(self):
        if not self.config.get_param("spotify_token"):
            return [
                MenuItem('Connect', action_name='spotify.connect', callback=self.auth_callback)
            ]
        else:
            menu = MenuItem('Devices', options=[])
            menu.add(MenuItem('default', action_name="spotify.device", callback=self.menu_callback, params={'id': None, 'name': 'default', 'volume_percent': 50}))
            devices = self.get_devices()
            for device in devices:
                print(device)
                menu.add(
                    MenuItem(device['name'], action_name="spotify.device", callback=self.menu_callback, params={'id': device['id'], 'name': device['name'], 'volume': device['volume_percent']})
                )
            return [menu]

    def get_devices(self):
        devices = self.spotify.devices()

        return devices['devices']

    def set_active_device(self):
        if self.config.get_param('spotify.use_active'):
            found = False
            devices = self.get_devices()
            for device in devices:
                if device['is_active']:
                    found = True
                    self.config.set_param('spotify.device', {'id': None, 'name': device['name'], 'volume': device['volume_percent']})
            if not found:
                self.config.set_param('spotify.device', {'id': None, 'name': self.config.get_param('spotify.no_device'), 'volume': 0})

    def increase_volume(self):
        device = self.config.get_param('spotify.device')
        if device['name'] != self.config.get_param('spotify.no_device'):
            device['volume'] += self.config.get_param('spotify.volume.step')
            if device['volume'] > 100:
                device['volume'] = 100
            self.config.set_param('spotify.device', device)
            self.spotify.volume(device['volume'], device['id'])

    def decrease_volume(self):
        device = self.config.get_param('spotify.device')
        if device['name'] != self.config.get_param('spotify.no_device'):
            device['volume'] -= self.config.get_param('spotify.volume.step')
            if device['volume'] < 0:
                device['volume'] = 0
            self.config.set_param('spotify.device', device)
            self.spotify.volume(device['volume'], device['id'])

    def shutdown(self):
        self.work = False

    def run(self):
        while self.work:
            start = time.time()
            if self.config.get_param("spotify_token"):
                playback = self.spotify.current_playback()
                print("fetch")
                print(playback)
                if playback:
                    self.data.set_data(playback)
            diff = (time.time() - start)
            time.sleep(self.fetch_tick - diff)
