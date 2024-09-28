from bluetooth.ble_scanner import *
from service.menu import Menu, MenuItem
import logging
import RPi.GPIO
from service.lcd import Display
from service.control import Control
from service.workflow import Workflow
from service.spotify import Spotify
import signal
from service.config import Config
from bluetooth.ble import BLE

RPi.GPIO.setmode(RPi.GPIO.BCM)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s %(message)s'
)
logger = logging.getLogger(__name__)

cfg = Config()
spotify = Spotify(cfg)
display = Display(cfg)
menu = Menu(cfg, display)
control = Control()
ble = BLE(cfg)

ble.lcd = display

workflow = Workflow(cfg, display, menu, spotify, ble)
menu.close_event = workflow.control_callback
control.callback = workflow.control_callback
spotify.auth_callback = workflow.menu_action
spotify.menu_callback = workflow.menu_action
ble.menu_callback = workflow.menu_action

menu.add_menu_item(MenuItem('Spotify', generator=spotify.get_menu))
menu.add_menu_item(MenuItem('BLE', generator=ble.get_menu))
menu.add_menu_item(MenuItem('Shutdown', action_name="sys.shutdown", callback=workflow.menu_action))

display.clear()
display.show_main()

spotify.start()


def shutdown():
    # menu.shutdown()
    spotify.shutdown()
    display.shutdown()
    control.shutdown()
    workflow.shutdown()


signal.signal(signal.SIGTERM, shutdown)

try:
    while workflow.app_works:
        time.sleep(1)
except KeyboardInterrupt:
    shutdown()

