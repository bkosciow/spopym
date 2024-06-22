from bluetooth.ble_scanner import *
from menu import Menu
import logging
import RPi.GPIO
from lcd import Display
from control import Control
from workflow import Workflow
from spotify import Spotify
import signal
from service.config import Config

RPi.GPIO.setmode(RPi.GPIO.BCM)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s %(message)s'
)
logger = logging.getLogger(__name__)


cfg = Config()

spotify = Spotify(cfg)
display = Display(cfg, spotify=spotify)
spotify.lcd = display

workflow = Workflow(display)

MENU_OPTIONS = [
    # {
    #     'name': 'First',
    #     'options': [
    #         {
    #             'name': 'Second',
    #             'options': [
    #                 {
    #                     'name': 'Third',
    #                     'options': [
    #                         {
    #                             'name': 'fourth',
    #                             'callback': workflow.menu_action
    #                         }
    #                     ]
    #                 }
    #             ]
    #         },
    #         {
    #             'name': 'Second  - two',
    #             'options': [
    #                 {
    #                     'name': '3rd from 2nd2',
    #                     'callback': workflow.menu_action
    #                 }
    #             ]
    #         }
    #     ]
    # },
    # {
    #     'name': 'Bluetooth',
    #     'options': [
    #         {
    #             'name': 'Rescan',
    #             'callback': workflow.menu_action,
    #         }
    #     ]
    # },
    {
        'name': 'Spotify',
        'generator': spotify.get_menu,
    },
    {
        'name': 'Shutdown',
        'callback': workflow.menu_action,
    },
]

menu = Menu(MENU_OPTIONS, display)
menu.close_event = workflow.control_callback
workflow.menu = menu

control = Control()
control.callback = workflow.control_callback

display.clear()
display.show_main()


def shutdown():
    # menu.shutdown()
    display.shutdown()
    control.shutdown()


signal.signal(signal.SIGTERM, shutdown)

try:
    while workflow.app_works:
        time.sleep(1)
except KeyboardInterrupt:
    shutdown()


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
