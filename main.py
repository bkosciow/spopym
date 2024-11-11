from service.menu import Menu, MenuItem
import logging
import RPi.GPIO
from service.display import Display
from service.control import Control
from service.workflow import Workflow
from service.spotify import Spotify
import signal
from service.config import Config
from service.ble import BLE
import time
from micro_storage.storage import Storage
from micro_storage.sqlite_engine import SQLiteEngine

RPi.GPIO.setmode(RPi.GPIO.BCM)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s %(message)s'
)
logger = logging.getLogger(__name__)

Storage.set_engine(SQLiteEngine())
storage = Storage()

cfg = Config()
spotify = Spotify(cfg)
display = Display(cfg)
menu = Menu(cfg, display)
control = Control()
ble = BLE(cfg, storage)

ble.lcd = display

workflow = Workflow(cfg, display, menu, spotify, ble)
menu.close_event = workflow.menu_action
control.callback = workflow.menu_action
spotify.auth_callback = workflow.menu_action
spotify.menu_callback = workflow.menu_action
ble.menu_callback = workflow.menu_action
spotify.add_track_callback(ble.broadcast_to_lcd)

menu.add_menu_item(MenuItem('Spotify', generator=spotify.get_menu))
menu.add_menu_item(MenuItem('BLE', generator=ble.get_menu))
menu.add_menu_item(MenuItem('Shutdown', action_name="sys.shutdown", callback=workflow.menu_action))

display.clear()
display.show_main()

spotify.start()
display.start()

ble.quick_scan()


def shutdown():
    # menu.shutdown()
    spotify.shutdown()
    display.shutdown()
    control.shutdown()
    workflow.shutdown()


signal.signal(signal.SIGTERM, shutdown)

try:
    while workflow.app_works:
        reads = ble.get_data()
        for uuid in reads:
            if reads[uuid] is not None:
                workflow.menu_action(reads[uuid], {'source': uuid})
        time.sleep(1)

except KeyboardInterrupt:
    logger.info('Shutting down')
    shutdown()
