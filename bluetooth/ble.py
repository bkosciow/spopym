from bluetooth.ble_scanner import *
from bluetooth.ble_device_manager import DeviceManager
from service.menu import MenuItem


class BLE:
    def __init__(self, config):
        self.menu_callback = None
        self.config = config
        self.config.set_param('ble_no_devices', 0)
        SERVICES = {
            '66b2c551-50df-4188-a436-d6858835fbe0': ['66b2c551-50df-4188-a436-d6858835fbe1',
                                                     '66b2c551-50df-4188-a436-d6858835fbe2'],
        }

        self.device_manager = DeviceManager()
        for service in SERVICES:
            self.device_manager.support_service(service, SERVICES[service])
            self.device_manager.add_alias('66b2c551-50df-4188-a436-d6858835fbe2', "lcd")
            self.device_manager.add_alias('66b2c551-50df-4188-a436-d6858835fbe1', "button")
            self.device_manager.add_alias('66b2c551-50df-4188-a436-d6858835fbe0', "player")

        self.scaner = Scanner(self.device_manager, _sleep=10)
        self.lcd = None

    def get_menu(self):
        menu = MenuItem('Scan',  action_name='ble.scan', callback=self.menu_callback)

        return [menu]

    def scan(self):
        self.menu_callback("lcd.show_popup", {"text": "Scanning"})
        self.scaner.scan()
        self.config.set_param('ble_no_devices', self.device_manager.count_devices())
        self.menu_callback("lcd.hide_popup")
