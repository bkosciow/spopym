import random
import time
import RPi.GPIO
from gfxlcd.driver.ssd1306.spi import SPI
from gfxlcd.driver.ssd1306.ssd1306 import SSD1306
from charlcd.buffered import CharLCD
from gfxlcd.driver.hd44780 import HD44780

from gpiozero import RotaryEncoder, Button

RPi.GPIO.setmode(RPi.GPIO.BCM)


class Display:
    def __init__(self):
        drv = SPI()
        lcd = SSD1306(128, 64, drv)
        lcd.init()

        drv = HD44780(lcd, True)
        print(drv.width, drv.height)
        self.lcd = CharLCD(drv.width, drv.height, drv, 0, 0)
        self.lcd.init()

    def __getattr__(self, attr):
        return getattr(self.lcd, attr)



#
# def action():
#     print(rotor.steps)
#
#
# def activate():
#     print("clicked")
#
#
# def back():
#     print("back")
#
#
# rotor.when_rotated = action
# btn.when_released = activate
# btn.when_held = back
#
#
# while True:
#     time.sleep(1)
