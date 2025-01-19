import spotipy
from spotipy.oauth2 import SpotifyOAuth
from service.track_data import TrackData
from service.menu import MenuItem
import threading
import time
import logging
import requests

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
        self.get_devices()
        self.play_modes = ["shuffle_state", "smart_shuffle", "repeat_state", "none"]
        self.play_mode_idx = None

    def add_track_callback(self, cb):
        self.track_callback.append(cb)

    def get_menu(self):
        if not self.config.get_param("spotify_token"):
            return [
                MenuItem('Connect', action_name='spotify.connect', callback=self.auth_callback)
            ]
        else:
            menu = MenuItem('Devices', options=[])
            menu.add(
                MenuItem('default', action_name="spotify.device", callback=self.menu_callback, params={'device': None})
            )
            devices = self.get_devices()
            for device in devices:
                logging.debug(device)
                menu.add(
                    MenuItem(device['name'], action_name="spotify.device", callback=self.menu_callback, params={'device': device})
                )
            return [menu]

    def get_devices(self):
        if not self.config.get_param('spotify_token'):
            return
        devices = self.spotify.devices()

        return devices['devices']

    def refresh_device_status(self):
        found = False
        saved_device = self.config.get_param('spotify.device')
        devices = self.get_devices()
        for device in devices:
            if self.config.get_param('spotify.use_active') and device['is_active']:
                found = True
                self.config.set_param('spotify.device', device)
                self.config.set_param('spotify.last_device', device)

            if not self.config.get_param('spotify.use_active') and saved_device and saved_device['id'] == device['id']:
                found = True
                self.config.set_param('spotify.device', device)
                self.config.set_param('spotify.last_device', device)

        if not found:
            self.config.set_param('spotify.device', None)

    def increase_volume(self):
        device = self.config.get_param('spotify.device')
        if device and device['supports_volume']:
            device['volume_percent'] += self.config.get_param('spotify.volume.step')
            if device['volume_percent'] > 100:
                device['volume_percent'] = 100
            self._safe_call(self.spotify.volume, {"volume_percent": device['volume_percent'], "device_id": device['id']})

    def decrease_volume(self):
        device = self.config.get_param('spotify.device')
        if device and device['supports_volume']:
            device['volume_percent'] -= self.config.get_param('spotify.volume.step')
            if device['volume_percent'] < 0:
                device['volume_percent'] = 0
            self.spotify.volume(device['volume_percent'], device['id'])
            self._safe_call(self.spotify.volume, {"volume_percent": device['volume_percent'], "device_id": device['id']})

    def next_track(self):
        device = self.config.get_param('spotify.device')
        if device:
            self._safe_call(self.spotify.next_track, {"device_id": device['id']})

    def prev_track(self):
        device = self.config.get_param('spotify.device')
        if device:
            self._safe_call(self.spotify.previous_track, {"device_id": device['id']})

    def start_play(self):
        device = self.config.get_param('spotify.last_device')
        if device is None:
            self.menu_callback('lcd.show_popup', {"text": 'No Device', 'close_delay': 3})
            return
        if not device['is_active']:
            self.transfer_playback(device)
        else:
            if device and not self.data.is_playing():
                self._safe_call(self.spotify.start_playback, {"device_id": device['id']})

    def pause_play(self):
        device = self.config.get_param('spotify.device')
        if device and self.data.is_playing():
            self._safe_call(self.spotify.pause_playback, {"device_id": device['id']})

    def transfer_playback(self, device):
        self._safe_call(self.spotify.transfer_playback, {"device_id": device['id']})

    def _safe_call(self, f, p=None):
        try:
            f(**p)
        except spotipy.exceptions.SpotifyException as e:
            logger.info(e.msg)
            logger.info(e.reason)
            logger.info(e.code)
            if e.reason == 'NO_ACTIVE_DEVICE':
                logger.debug('No active device')
                self.menu_callback('lcd.show_popup', {"text": 'No Device', 'close_delay': 3})
            if e.reason == 'UNKNOWN':
                logger.debug('Duplicated call?')
            if e.reason == 'NONE' and e.code == 404:
                logger.debug('no device')
                self.menu_callback('lcd.show_popup', {"text": 'No Device', 'close_delay': 3})
            if e.code == 403 and 'Player command failed: Restriction violated' in e.msg:
                self.transfer_playback(self.config.get_param('spotify.device'))
                self._safe_call(f, p)
        except requests.exceptions.ConnectionError as e:
            print("Connection aborted")

    def set_device(self, device):
        if device is None:
            self.config.set_param('spotify.use_active', True)
        else:
            self.config.set_param('spotify.use_active', False)
            self.config.set_param('spotify.device', device)
            self.config.set_param('spotify.last_device', device)
            self.transfer_playback(device)

    def shutdown(self):
        self.work = False

    def run(self):
        while self.work:
            start = time.time()
            if self.config.get_param("spotify_token"):
                try:
                    self.refresh_device_status()
                    playback = self.spotify.current_playback()
                    if playback:
                        self.data.set_data(playback)
                        for cb in self.track_callback:
                            cb(self.data)
                except requests.exceptions.ReadTimeout as e:
                    logger.info("API timeout")
                except requests.exceptions.ConnectionError as e:
                    logger.info("Connection aborted.")
                    print("Connection aborted")

            diff = (time.time() - start)
            if self.fetch_tick - diff > 0:
                time.sleep(self.fetch_tick - diff)
