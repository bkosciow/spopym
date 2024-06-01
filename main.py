import random
import time
from ble_device_manager import DeviceManager
from ble_scanner import *
from menu import Menu
import logging
import RPi.GPIO
from lcd import Display
from gpiozero import RotaryEncoder, Button

RPi.GPIO.setmode(RPi.GPIO.BCM)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s %(message)s'
)
logger = logging.getLogger(__name__)

rotor = RotaryEncoder(19, 26, wrap=True, max_steps=180)
btn = Button(21, pull_up=False)

display = Display()

encoder_last = 0

def menu_click(name):
    print(name)


MENU_OPTIONS = [
    {
        'name': 'First',
        'callback': menu_click
    },
    {
        'name': 'Bluetooth',
        'options': [
            {
                'name': 'Rescan',
                'callback': menu_click,
            }
        ]
    },
    {
        'name': 'Shutdown',
        'callback': menu_click,
    },
]
menu = Menu(MENU_OPTIONS, display)


def rotate_encoder():
    global encoder_last
    if encoder_last < rotor.steps:
        menu.move_down()
    else:
        menu.move_up()
    encoder_last = rotor.steps
    print(rotor.steps)


def activate():
    menu.activate()
    print("clicked")


rotor.when_rotated = rotate_encoder
btn.when_released = activate


menu.start()

while True:
    time.sleep(1)

# menu.move_down()
# menu.move_down()

# SERVICES = {
#     '66b2c551-50df-4188-a436-d6858835fbe0': ['66b2c551-50df-4188-a436-d6858835fbe1', '66b2c551-50df-4188-a436-d6858835fbe2'],
# }
#
# deviceManger = DeviceManager()
# scanerThread = Scanner(deviceManger, _sleep=10)
#
# for service in SERVICES:
#     deviceManger.support_service(service, SERVICES[service])
#
# deviceManger.add_alias('66b2c551-50df-4188-a436-d6858835fbe2', "lcd")
# deviceManger.add_alias('66b2c551-50df-4188-a436-d6858835fbe1', "button")
# deviceManger.add_alias('66b2c551-50df-4188-a436-d6858835fbe0', "player")
#
# SCAN_TIME = 3
#
# scanerThread.start()
#
# time.sleep(0.5)
# while True:
#     nots = deviceManger.get_notifications(0.100)
#     print(nots)
#     if random.randint(0, 10) > 7:
#         d = time.asctime()
#         deviceManger.write_to_characteristic('66b2c551-50df-4188-a436-d6858835fbe2', bytes(d+"\n", "utf-8"))
#
#     time.sleep(0.2)
