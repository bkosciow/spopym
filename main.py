from bluetooth.ble_scanner import *
from service.menu import Menu
import logging
import RPi.GPIO
from service.lcd import Display
from control import Control
from service.workflow import Workflow
from service.spotify import Spotify
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
display = Display(cfg)
# spotify.lcd = display

menu = Menu(cfg, display)
workflow = Workflow(cfg, display, menu, spotify)
menu.close_event = workflow.control_callback

control = Control()
control.callback = workflow.control_callback

spotify.auth_callback = workflow.control_callback

MENU_OPTIONS = [
    {
        'name': 'Spotify',
        'generator': spotify.get_menu,
    },
    {
        'name': 'Shutdown',
        'callback': workflow.menu_action,
    },
]

menu.add_menu(MENU_OPTIONS)

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
