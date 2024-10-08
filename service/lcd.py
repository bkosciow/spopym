import RPi.GPIO
from gfxlcd.driver.ssd1306.spi import SPI
from gfxlcd.driver.ssd1306.ssd1306 import SSD1306
from charlcd.buffered import CharLCD
from gfxlcd.driver.hd44780 import HD44780
from subprocess import check_output
RPi.GPIO.setmode(RPi.GPIO.BCM)


class Display:
    def __init__(self, config):
        self.saved_lcd = None
        self.config = config
        drv = SPI()
        self.size = (128, 64)
        self.raw_lcd = SSD1306(self.size[0], self.size[1], drv)
        self.raw_lcd.init()

        drv = HD44780(self.raw_lcd, True)
        self.lcd = CharLCD(drv.width, drv.height, drv, 0, 0)
        self.lcd.init()

    def __getattr__(self, attr):
        return getattr(self.lcd, attr)

    def show_main(self):
        ip = check_output(['hostname', '-I']).decode('utf8')
        self.lcd.write(ip.strip(), 0, 0)
        bottom_bar = ""
        if not self.config.get_param("spotify_token"):
            self.lcd.write("Spotify: D/C", 0, 2)
            bottom_bar = "[ ]" + bottom_bar
        else:
            self.lcd.write(self.config.get_param('spotify.device')['name'].ljust(self.lcd.width), 0, 6)
            self.lcd.write(str(self.config.get_param('spotify.device')['volume']).ljust(3), 0, 7)
            bottom_bar = "[S]" + bottom_bar

        if self.config.get_param('use_message'):
            bottom_bar = "[M]" + bottom_bar

        bottom_bar = "[" + str(self.config.get_param('ble_no_devices')) + "]" + bottom_bar
        self.lcd.write(bottom_bar, 16 - len(bottom_bar), 7)
        self.lcd.flush(True)

    def show_authorize(self):
        self.lcd.write("Go to terminal", 0, 1)
        self.lcd.write("and run: ", 0, 2)
        self.lcd.write("auth.py", 2, 4)

        self.lcd.write("Then restart app", 0, 6)
        self.lcd.flush(True)

    def shutdown(self):
        self.clear()
        self.lcd.write("Goodbye", 4, 4)
        self.lcd.flush(True)

    def clear(self):
        for i in range(0, self.lcd.height):
            self.lcd.write(" " * self.lcd.width, 0, i)
        self.lcd.flush(True)

    def save_screen(self):
        self.saved_lcd = self.lcd.buffer.copy()

    def show_popup(self, text):
        x_offset = (self.lcd.width - len(text)) // 2
        x_offset -= 2
        y_offset = 2
        self.lcd.write("*" * (len(text)+4), x_offset, y_offset)
        self.lcd.write("* " + (" "*len(text)) + " *", x_offset, y_offset + 1)
        self.lcd.write("* " + text + " *", x_offset, y_offset + 2)
        self.lcd.write("* " + (" " * len(text)) + " *", x_offset, y_offset + 3)
        self.lcd.write("*" * (len(text) + 4), x_offset, y_offset + 4)
        self.lcd.flush()

    def restore_screen(self):
        self.lcd.buffer = self.saved_lcd
        self.lcd.dirty = True
        self.lcd.flush()
