import random
import time
from ble_device_manager import DeviceManager
from ble_scanner import *
from menu import Menu
import logging
import RPi.GPIO
from lcd import Display
from control import Control

RPi.GPIO.setmode(RPi.GPIO.BCM)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s %(message)s'
)
logger = logging.getLogger(__name__)


class Workflow:
    def __init__(self, menu=None):
        self.menu = menu
        self.state = 'main'

    def control_callback(self, action):
        print("control_callback ", action)
        if action == 'encoder_click':
            if self.state == 'main':
                self.state = 'menu'
                self.menu.start()
            elif self.state == 'menu':
                self.menu.activate()

        if action == 'encoder_inc':
            if self.state == 'menu':
                self.menu.move_up()

        if action == 'encoder_dec':
            if self.state == 'menu':
                self.menu.move_down()

    def menu_action(self, name):
        print("menu_action ", name)



workflow = Workflow()

MENU_OPTIONS = [
    {
        'name': 'First',
        'options': [
            {
                'name': 'Second',
                'options': [
                    {
                        'name': 'Third',
                        'options': [
                            {
                                'name': 'fourth',
                                'callback': workflow.menu_action
                            }
                        ]
                    }
                ]
            }
        ]
        # 'callback': workflow.menu_action
    },
    {
        'name': 'Bluetooth',
        'options': [
            {
                'name': 'Rescan',
                'callback': workflow.menu_action,
            }
        ]
    },
    {
        'name': 'Shutdown',
        'callback': workflow.menu_action,
    },
]

display = Display()
menu = Menu(MENU_OPTIONS, display)
workflow.menu = menu
control = Control()
control.callback = workflow.control_callback

display.clear()
display.show_main()

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
