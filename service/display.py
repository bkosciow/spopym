import RPi.GPIO
from gfxlcd.driver.ssd1306.spi import SPI
from gfxlcd.driver.ssd1306.ssd1306 import SSD1306
from charlcd.buffered import CharLCD
from gfxlcd.driver.hd44780 import HD44780
from subprocess import check_output
import threading
import time
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


class Display(threading.Thread):
    def __init__(self, config, refresh_tick=0.2):
        super().__init__()
        self.refresh_tick = refresh_tick
        self.saved_content = None
        self.config = config

        drv = SPI()
        self.size = (128, 64)
        self.raw_lcd = SSD1306(self.size[0], self.size[1], drv)
        self.raw_lcd.init()
        drv = HD44780(self.raw_lcd, True)
        self.lcd = CharLCD(drv.width, drv.height, drv, 0, 0)
        self.lcd.init()

        self.menu_top_offset = 1
        self.menu_content_height = self.lcd.height - 2

        self.work = True
        self.popup = None

    def show_main(self):
        ip = check_output(['hostname', '-I']).decode('utf8')
        self.lcd.write(ip.strip(), 0, 0)
        bottom_bar = ""
        if not self.config.get_param("spotify_token"):
            self.lcd.write("Spotify: D/C", 0, 2)
            bottom_bar = "[ ]" + bottom_bar
        else:
            device_name = self.config.get_param('spotify.device')['name'] if self.config.get_param('spotify.device') else '----'
            volume = self.config.get_param('spotify.device')['volume_percent'] if self.config.get_param('spotify.device') else '--'
            self.lcd.write(device_name.ljust(self.lcd.width), 0, 6)
            self.lcd.write(str(volume).ljust(3), 0, 7)
            bottom_bar = "[S]" + bottom_bar

        if self.config.get_param('use_message'):
            bottom_bar = "[M]" + bottom_bar

        bottom_bar = "[" + str(self.config.get_param('ble_no_devices')) + "]" + bottom_bar
        self.lcd.write(bottom_bar, 16 - len(bottom_bar), 7)

    def show_authorize(self):
        self.lcd.write("Go to terminal", 0, 1)
        self.lcd.write("and run: ", 0, 2)
        self.lcd.write("auth.py", 2, 4)

        self.lcd.write("Then restart app", 0, 6)

    def shutdown(self):
        self.work = False
        self.clear()
        self.lcd.write("Goodbye", 4, 4)
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
        x_offset -= 2
        y_offset = 2
        self.lcd.write("*" * (len(text) + 4), x_offset, y_offset)
        self.lcd.write("* " + (" " * len(text)) + " *", x_offset, y_offset + 1)
        self.lcd.write("* " + text + " *", x_offset, y_offset + 2)
        self.lcd.write("* " + (" " * len(text)) + " *", x_offset, y_offset + 3)
        self.lcd.write("*" * (len(text) + 4), x_offset, y_offset + 4)

    def show_menu(self, menu, clear, selected_position):
        begin = (selected_position // self.menu_content_height) * self.menu_content_height
        end = begin + self.menu_content_height
        if clear:
            self.clear()

        menu = menu[begin:end]
        idx = 0
        for item in menu:
            self.lcd.write(item + " " * (self.lcd.width-len(item)), 0, idx + self.menu_top_offset)
            idx += 1
        for i in range(idx, self.menu_content_height):
            self.lcd.write(" " * self.lcd.width, 0, i + self.menu_top_offset)

    def refresh_lcd(self):
        if self.config.get_param('state') == 'main':
            self.show_main()

    def run(self):
        while self.work:
            start = time.time()
            self.refresh_lcd()
            if self.popup:
                self.popup.tick()
            if self.popup:
                self.refresh_popup()
            self.lcd.flush(True)
            diff = (time.time() - start)
            if self.refresh_tick - diff > 0:
                time.sleep(self.refresh_tick - diff)
