import bluepy.btle as btle
import threading
import time
import logging
logger = logging.getLogger(__name__)


def scan(length=3):
    scanner = btle.Scanner()
    devices = None

    try:
        devices = scanner.scan(length)
    except btle.BTLEDisconnectError:
        pass

    return devices


class Scanner(threading.Thread):
    def __init__(self, device_manager, _time=3, _sleep=60):
        super().__init__()
        self.ignore_macs = []
        self.device_manager = device_manager
        self.work = True
        self.time = _time
        self.sleep = _sleep

    def _scan(self):
        devices = None
        while not devices:
            devices = scan(self.time)
            time.sleep(0.5)

        return devices

    def scan(self):
        logging.debug("executing scan")
        devices = self._scan()
        for dev in devices:
            logging.debug("found %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
            if not self.device_manager.exists(dev) and self.device_manager.add_if_supported(dev):
                logging.debug('Adding device %s to manager: ', dev.addr)

    def run(self):
        while self.work:
            self.scan()
            time.sleep(self.sleep)

    def stop(self):
        self.work = False


