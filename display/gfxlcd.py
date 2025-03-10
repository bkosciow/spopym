import RPi.GPIO
from charlcd.buffered import CharLCD
from gfxlcd.driver.hd44780 import HD44780
from subprocess import check_output
from service.action_interface import ActionInterface
import threading
import time
import pathlib
import json
from display.text import TextScroll
import textwrap
from importlib import import_module
RPi.GPIO.setmode(RPi.GPIO.BCM)


class Popup:
    def __init__(self, text, display, close_delay=None):
        self.text = text
        self.display = display
        self.close_delay = close_delay
        if close_delay:
            self.close_time = time.time() + close_delay

    def get_text(self):
        return self.text

    def tick(self):
        if self.close_delay:
            if time.time() > self.close_time:
                self.display.hide_popup()


class GFXLCD(threading.Thread, ActionInterface):
    def __init__(self, config, storage):
        super().__init__()
        ActionInterface.__init__(self, config)
        self.display_locked = False
        self.storage = storage
        self.refresh_tick = 0.2
        self.saved_content = None
        self.track_data = None
        self.additional = {
            "data": {
                'ip': '- - -',
                'temp': '?',
            },
            "tick": 10,
            'last': 0.0,
            'title': None,
            'artist': None,
            'track_data': None,
        }
        self.main_screen = {
            'current': self.storage.get("display.main") if self.storage.get("display.main") else 0,
            'count': 2,
        }

        drv_name = (pathlib.Path(self.config.get('display.driver')).suffix[1:]).upper()
        drv_class = getattr(import_module(self.config.get('display.driver')), drv_name)
        drv_params = json.loads(self.config.get('display.driver_params'))
        drv = drv_class(**drv_params)

        device_name = (pathlib.Path(self.config.get('display.device')).suffix[1:]).upper()
        device_class = getattr(import_module(self.config.get('display.device')), device_name)

        self.size = self.config.get('display.device_size').split(",")

        self.raw_lcd = device_class(int(self.size[0]), int(self.size[1]), drv)
        self.raw_lcd.rotation = int(self.config.get('display.device_rotation'))

        xy_callback = self.config.get('display.xy_callback')
        if xy_callback:
            module_path, func_name = xy_callback.rsplit('.', 1)
            self.raw_lcd.xy_callback = getattr(import_module(module_path), func_name)

        self._init_display()

        self.offsets = list(map(int, self.config.get('display.device_offset').split(",")))

        self.menu_top_offset = 1 + self.offsets[1]
        self.menu_content_height = self.lcd.height - 2 - self.offsets[1]

        self.additional['title'] = TextScroll("- - -", self.lcd.width - self.offsets[0])
        self.additional['artist'] = TextScroll("- - -", self.lcd.width - self.offsets[0])

        self.work = True
        self.popup = None
        self.last_state = None

    def _init_display(self):
        self.raw_lcd.init()

        drv = HD44780(self.raw_lcd, True)
        self.lcd = CharLCD(drv.width, drv.height, drv, 0, 0)
        self.lcd.init()

    def fetch_additional_data(self):
        self.additional['data']['ip'] = check_output(['hostname', '-I']).decode('utf8')
        self.additional['data']['temp'] = check_output(['vcgencmd', 'measure_temp']).decode('utf8').replace('temp=', '').split('.')[0]

    def set_track_data(self, track_data):
        self.track_data = track_data
        data = track_data.get_data()
        self.additional['title'].set_text(data['title'])
        self.additional['artist'].set_text(data['artist'])
        self.additional['track_data'] = data

    def time_to_display(self, data, filler="0"):
        if data < 0:
            data = filler * 2
        elif data < 10:
            data = filler + str(data)
        elif data > 99:
            data = "99"
        else:
            data = str(data)

        return data

    def show_main(self):
        bottom_bar = []

        if self.main_screen['current'] == 0:
            self.lcd.write(self.additional['data']['ip'].strip(), 0+self.offsets[0], 0+self.offsets[1])
            bottom_bar.append(self.additional['data']['temp'])
            bottom_bar.append(str(self.config.get_param('ble_no_devices')))
            if not self.config.get_param("spotify_token"):
                self.lcd.write("Spotify: D/C", 0+self.offsets[0], 2+self.offsets[1])
            else:
                device_name = self.config.get_param('spotify.device')['name'] if self.config.get_param('spotify.device') else '----'
                volume = self.config.get_param('spotify.device')['volume_percent'] if self.config.get_param('spotify.device') else '--'
                self.lcd.write(device_name.ljust(self.lcd.width), 0+self.offsets[0], 6+self.offsets[1])
                self.lcd.write(str(volume).ljust(3), 0+self.offsets[0], 7+self.offsets[1])
                bottom_bar.append("S")

            if self.config.get_param('use_message'):
                bottom_bar.append("M")
            bottom_bar = "|".join(bottom_bar)
            self.lcd.write(bottom_bar, 16 - len(bottom_bar), 7 + self.offsets[1])

        if self.main_screen['current'] == 1:
            if not self.config.get_param("spotify_token"):
                self.lcd.write("Spotify: D/C", 0+self.offsets[0], 2+self.offsets[1])
            else:
                device_name = self.config.get_param('spotify.device')['name'] if self.config.get_param('spotify.device') else '----'
                volume = self.config.get_param('spotify.device')['volume_percent'] if self.config.get_param('spotify.device') else '--'
                bottom_bar.append(str(volume).ljust(2))
                bottom_bar.append(device_name)
                self.lcd.write(self.additional['artist'].get_tick(), 0 + self.offsets[0], 0 + self.offsets[1])
                self.lcd.write(self.additional['title'].get_tick(), 0 + self.offsets[0], 2 + self.offsets[1])
                progress_bar = '[' + " " * (self.lcd.width - self.offsets[0] - 2) + ']'
                self.lcd.write(progress_bar, 0 + self.offsets[0], 5)
                if self.additional['track_data'] is not None:
                    progress = int(self.additional['track_data']['progress'] * 100 / self.additional['track_data']['length'])
                    offset = round(progress * len(progress_bar) / 100)
                    if offset == len(progress_bar):
                        offset -= 1
                    self.lcd.write("#", 0 + self.offsets[0] + offset, 5)

            bottom_bar = " ".join(bottom_bar)
            if len(bottom_bar) < self.lcd.width - self.offsets[0]:
                bottom_bar += " " * (self.lcd.width - self.offsets[0]-len(bottom_bar))
            self.lcd.write(bottom_bar, 0+self.offsets[0], 7 + self.offsets[1])

    def show_authorize(self):
        self.lcd.write("Go to terminal", 0+self.offsets[0], 1+self.offsets[1])
        self.lcd.write("and run: ", 0+self.offsets[0], 2+self.offsets[1])
        self.lcd.write("auth.py", 2+self.offsets[0], 4+self.offsets[1])

        self.lcd.write("Then restart app", 0+self.offsets[0], 6+self.offsets[1])

    def shutdown(self):
        self.work = False
        self.clear()
        self.lcd.write("Goodbye", 4+self.offsets[0], 4+self.offsets[1])
        self.lcd.flush(True)

    def clear(self):
        for i in range(0, self.lcd.height):
            self.lcd.write(" " * self.lcd.width, 0, i)

    def show_popup(self, text, close_delay=None):
        self.popup = Popup(text, self, close_delay)
        self.saved_content = self.lcd.buffer.copy()

    def hide_popup(self):
        self.popup = None
        self.lcd.buffer = self.saved_content

    def refresh_popup(self):
        text = self.popup.get_text()
        x_offset = (self.lcd.width - len(text)) // 2
        x_offset -= 2 + self.offsets[0]
        y_offset = 2 + self.offsets[1]
        self.lcd.write("*" * (len(text) + 4), x_offset, y_offset)
        self.lcd.write("* " + (" " * len(text)) + " *", x_offset, y_offset + 1)
        self.lcd.write("* " + text + " *", x_offset, y_offset + 2)
        self.lcd.write("* " + (" " * len(text)) + " *", x_offset, y_offset + 3)
        self.lcd.write("*" * (len(text) + 4), x_offset, y_offset + 4)

    def show_menu(self):
        menu = self.config.get_param("menu.menu")
        selected_position = self.config.get_param("menu.position")
        begin = (selected_position // self.menu_content_height) * self.menu_content_height
        end = begin + self.menu_content_height

        menu = menu[begin:end]
        idx = 0
        for item in menu:
            self.lcd.write(item + " " * (self.lcd.width-len(item)), 0+self.offsets[0], idx + self.menu_top_offset)
            idx += 1
        for i in range(idx, self.menu_content_height):
            self.lcd.write(" " * self.lcd.width, 0+self.offsets[0], i + self.menu_top_offset)

    def show_pattern_set(self):
        self.clear()
        self.lcd.write("Set unlock", 1 + self.offsets[0], 1 + self.offsets[1])
        self.lcd.write("pattern", 1 + self.offsets[0], 2 + self.offsets[1])
        last = self.config.get_param('last_button')
        if last is not None:
            self.lcd.write(last, 1 + self.offsets[0], 4 + self.offsets[1])

    def show_device_locked(self):
        self.clear()
        self.lcd.write("Device locked", 1 + self.offsets[0], 1 + self.offsets[1])
        self.lcd.write("Enter unlock", 1 + self.offsets[0], 2 + self.offsets[1])
        self.lcd.write("pattern", 1 + self.offsets[0], 3 + self.offsets[1])

    def refresh_lcd(self):
        if self.last_state != self.config.get_param('state'):
            self.last_state = self.config.get_param('state')
            self.clear()

        if self.config.get_param('state') == 'main':
            self.show_main()

        if self.config.get_param('state') == 'set_pattern':
            self.show_pattern_set()

        if self.config.get_param('state') == 'menu':
            self.show_menu()

        if self.config.get_param('state') == 'device.locked':
            self.show_device_locked()

    def run(self):
        while self.work:
            start = time.time()
            if self.additional['last'] + self.additional['tick'] < start:
                self.additional['last'] = start
                self.fetch_additional_data()

            self.refresh_lcd()
            if self.popup:
                self.popup.tick()
            if self.popup:
                self.refresh_popup()
            if not self.display_locked:
                self.lcd.flush(True)
            diff = (time.time() - start)
            if self.refresh_tick - diff > 0:
                time.sleep(self.refresh_tick - diff)

    def handle_action(self, state, action, params):
        if action == 'sys.shutdown':
            self.shutdown()
        if state == 'device.locked':
            return
        if action == 'BTN_RESET_LCD':
            self.display_locked = True
            time.sleep(0.5)
            self._init_display()
            self.display_locked = False
        if action == 'close_menu' or action == 'BTN_HOME':
            if state == 'menu':
                self.set_state('main')
                self.clear()
                self.show_main()
            if state == 'main':
                self.main_screen['current'] += 1
                if self.main_screen['current'] == self.main_screen['count']:
                    self.main_screen['current'] = 0
                self.storage.set("display.main", self.main_screen['current'])
                self.clear()

        if action == 'lcd.show_popup':
            self.show_popup(
                text=params['text'],
                close_delay=params['close_delay'] if 'close_delay' in params else None
            )

        if action == 'lcd.hide_popup':
            self.hide_popup()

        if action == 'spotify.connect':
            self.show_authorize()

