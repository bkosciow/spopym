import random
import time
from ble_device_manager import DeviceManager
from ble_scanner import *
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s %(message)s'
)
logger = logging.getLogger(__name__)


SERVICES = {
    '66b2c551-50df-4188-a436-d6858835fbe0': ['66b2c551-50df-4188-a436-d6858835fbe1', '66b2c551-50df-4188-a436-d6858835fbe2'],
}

deviceManger = DeviceManager()
scanerThread = Scanner(deviceManger, _sleep=10)

for service in SERVICES:
    deviceManger.support_service(service, SERVICES[service])

deviceManger.add_alias('66b2c551-50df-4188-a436-d6858835fbe2', "lcd")
deviceManger.add_alias('66b2c551-50df-4188-a436-d6858835fbe1', "button")
deviceManger.add_alias('66b2c551-50df-4188-a436-d6858835fbe0', "player")

SCAN_TIME = 3

scanerThread.start()

time.sleep(0.5)
while True:
    nots = deviceManger.get_notifications(0.100)
    print(nots)
    if random.randint(0, 10) > 7:
        d = time.asctime()
        deviceManger.write_to_characteristic('66b2c551-50df-4188-a436-d6858835fbe2', bytes(d+"\n", "utf-8"))

    time.sleep(0.2)
