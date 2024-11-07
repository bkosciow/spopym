import spotipy
from spotipy.oauth2 import SpotifyOAuth
from service.track_data import TrackData
from service.menu import MenuItem
import threading
import time
import logging

logger = logging.getLogger(__name__)


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
        self.track_callback = []
        if self.config.get_param('spotify_token'):
            self.get_devices()

    def add_track_callback(self, cb):
        self.track_callback.append(cb)

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
                logging.debug(device)
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
                    self.config.set_param('spotify.device', {'id': device['id'], 'name': device['name'], 'volume': device['volume_percent']})
                    self.config.set_param('spotify.last_device', {'id': device['id'], 'name': device['name'], 'volume': device['volume_percent']})
            if not found:
                self.config.set_param('spotify.device', {'id': None, 'name': self.config.get_param('spotify.no_device'), 'volume': 0})

    def increase_volume(self):
        device = self.config.get_param('spotify.device')
        if device['id']:
            device['volume'] += self.config.get_param('spotify.volume.step')
            if device['volume'] > 100:
                device['volume'] = 100
            self._safe_call(self.spotify.volume, {"volume_percent": device['volume'], "device_id": device['id']})

    def decrease_volume(self):
        device = self.config.get_param('spotify.device')
        if device['id']:
            device['volume'] -= self.config.get_param('spotify.volume.step')
            if device['volume'] < 0:
                device['volume'] = 0
            self.spotify.volume(device['volume'], device['id'])
            self._safe_call(self.spotify.volume, {"volume_percent": device['volume'], "device_id": device['id']})

    def next_track(self):
        device = self.config.get_param('spotify.device')
        if device['id']:
            self._safe_call(self.spotify.next_track, {"device_id": device['id']})

    def prev_track(self):
        device = self.config.get_param('spotify.device')
        if device['id']:
            self._safe_call(self.spotify.previous_track, {"device_id": device['id']})

    def start_play(self):
        device = self.config.get_param('spotify.last_device')
        if device['id'] and not self.data.is_playing():
            self._safe_call(self.spotify.start_playback, {"device_id": device['id']})

    def pause_play(self):
        device = self.config.get_param('spotify.device')
        if device['id'] and self.data.is_playing():
            self._safe_call(self.spotify.pause_playback, {"device_id": device['id']})

    def _safe_call(self, f, p=None):
        try:
            f(**p)
        except spotipy.exceptions.SpotifyException as e:
            logger.info(e.msg)
            if e.reason == 'NO_ACTIVE_DEVICE':
                logger.debug('No active device')
            if e.reason == 'UNKNOWN':
                logger.debug('Duplicated call?')
            if e.reason == 'NONE' and e.code == 404:
                logger.debug('no device')

    def shutdown(self):
        self.work = False

    def run(self):
        while self.work:
            start = time.time()
            if self.config.get_param("spotify_token"):
                playback = self.spotify.current_playback()
                if playback:
                    self.data.set_data(playback)
                    for cb in self.track_callback:
                        cb(self.data)
            diff = (time.time() - start)
            if self.fetch_tick - diff > 0:
                time.sleep(self.fetch_tick - diff)
