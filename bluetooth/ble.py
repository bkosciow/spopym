from bluetooth.ble_scanner import *
from bluetooth.ble_device_manager import DeviceManager
import random
from service.menu import MenuItem


class BLE:
    def __init__(self):
        self.menu_callback = None
        SERVICES = {
            '66b2c551-50df-4188-a436-d6858835fbe0': ['66b2c551-50df-4188-a436-d6858835fbe1',
                                                     '66b2c551-50df-4188-a436-d6858835fbe2'],
        }

        self.device_manger = DeviceManager()
        for service in SERVICES:
            self.device_manger.support_service(service, SERVICES[service])
            self.device_manger.add_alias('66b2c551-50df-4188-a436-d6858835fbe2', "lcd")
            self.device_manger.add_alias('66b2c551-50df-4188-a436-d6858835fbe1', "button")
            self.device_manger.add_alias('66b2c551-50df-4188-a436-d6858835fbe0', "player")

        self.scaner = Scanner(self.device_manger, _sleep=10)

    def get_menu(self):
        menu = MenuItem('Scan',  action_name='ble.scan', callback=self.menu_callback)

        return [menu]

    def scan(self):
        print("scan")
        self.scaner.scan()
        print('stop scan')
