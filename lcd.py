import RPi.GPIO
from gfxlcd.driver.ssd1306.spi import SPI
from gfxlcd.driver.ssd1306.ssd1306 import SSD1306
from charlcd.buffered import CharLCD
from gfxlcd.driver.hd44780 import HD44780

RPi.GPIO.setmode(RPi.GPIO.BCM)


class Display:
    def __init__(self):
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
        self.lcd.write("Main", 5, 0)
        self.lcd.write("Devices: ", 0, 1)
        self.lcd.write("IP: ", 0, 2)
        self.lcd.flush(True)

    def clear(self):
        for i in range(0, self.lcd.height-1):
            self.lcd.write(" "*(self.lcd.width-1), 0, i)
        self.lcd.flush(True)
