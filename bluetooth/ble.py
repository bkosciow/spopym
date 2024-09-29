from bluetooth.ble_scanner import *
from bluetooth.ble_device_manager import DeviceManager
from service.menu import MenuItem

DEVICE = '66b2c551-50df-4188-a436-d6858835fbe0'
DEVICE_LCD = '66b2c551-50df-4188-a436-d6858835fbe2'
DEVICE_BUTTONS = '66b2c551-50df-4188-a436-d6858835fbe1'
SERVICES = {
    DEVICE: [DEVICE_BUTTONS, DEVICE_LCD],
}


class BLE:
    def __init__(self, config):
        self.menu_callback = None
        self.config = config
        self.config.set_param('ble_no_devices', 0)
        self.device_manager = DeviceManager()
        for service in SERVICES:
            self.device_manager.support_service(service, SERVICES[service])
            self.device_manager.add_alias(DEVICE_LCD, "lcd")
            self.device_manager.add_alias(DEVICE_BUTTONS, "button")
            self.device_manager.add_alias(DEVICE, "player")

        self.scaner = Scanner(self.device_manager, _sleep=10)
        self.lcd = None
        self.cache = {}
        self.mtu = 18

    def get_menu(self):
        menu = MenuItem('Scan',  action_name='ble.scan', callback=self.menu_callback)

        return [menu]

    def scan(self):
        self.menu_callback("lcd.show_popup", {"text": "Scanning"})
        self.scaner.scan()
        self.config.set_param('ble_no_devices', self.device_manager.count_devices())
        self.menu_callback("lcd.hide_popup")
        self.cache = {}

    def broadcast_to_lcd(self, track_data):
        data = track_data.get_data()
        for k, v in data.items():
            if k not in self.cache or v != self.cache[k]:
                self.cache[k] = v
                pos = 0
                packet_data = str(v)
                data_chunk = packet_data[0:self.mtu]
                while data_chunk:
                    message = str(track_data.get_code_for_key(k)) + str(pos) + data_chunk
                    print(pos, message)
                    self.device_manager.write_to_characteristic(DEVICE_LCD, bytes(message, "utf-8"))
                    pos += 1
                    data_chunk = str(v)[pos*self.mtu:(pos+1)*self.mtu]
