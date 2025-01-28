from micro_ble.ble_helper import BLEHelper
from service.menu import MenuItem
import bluepy
from service.action_interface import ActionInterface

DEVICE = '66b2c551-50df-4188-a436-d6858835fbe0'
DEVICE_LCD = '66b2c551-50df-4188-a436-d6858835fbe2'
DEVICE_BUTTONS = '66b2c551-50df-4188-a436-d6858835fbe1'
SERVICES = {
    DEVICE: [DEVICE_BUTTONS, DEVICE_LCD],
}

KEY_LAST_DEVICES = 'last_ble_devices'


class BLE(ActionInterface):
    def __init__(self, config, storage):
        ActionInterface.__init__(self, config)
        self.menu_callback = None
        self.storage = storage
        self.config.set_param('ble_no_devices', 0)
        self.ble_helper = BLEHelper()
        for service in SERVICES:
            self.ble_helper.support_service(service, SERVICES[service])

        self.cache = {}
        self.mtu = 18

    def get_menu(self):
        menu = MenuItem('Scan',  action_name='ble.scan', callback=self.menu_callback)

        return [menu]

    def scan(self):
        self.menu_callback("lcd.show_popup", {"text": "Scanning"})
        try:
            addresses = self.ble_helper.scan()
            self.storage.set(KEY_LAST_DEVICES, addresses)
            self.config.set_param('ble_no_devices', self.ble_helper.count_devices())
            self.menu_callback("lcd.hide_popup")
        except bluepy.btle.BTLEManagementError as e:
            self.menu_callback("lcd.hide_popup")
            if e.estat == 20:
                self.menu_callback("lcd.show_popup", {"text": "Root req", "close_delay": 3})

        self.cache = {}

    def quick_scan(self):
        last_devices = self.storage.get(KEY_LAST_DEVICES)
        if last_devices is not None:
            self.menu_callback("lcd.show_popup", {"text": "Reconnect"})
            self.ble_helper.scan(last_devices)
            self.config.set_param('ble_no_devices', self.ble_helper.count_devices())
            self.menu_callback("lcd.hide_popup")
            self.cache = {}

    def broadcast_to_lcd(self, track_data):
        if not self.ble_helper.enabled:
            return
        data = track_data.get_data()
        for k, v in data.items():
            if k not in self.cache or v != self.cache[k]:
                self.cache[k] = v
                pos = 0
                packet_data = str(v)
                data_chunk = packet_data[0:self.mtu]
                while data_chunk:
                    message = str(track_data.get_code_for_key(k)) + str(pos) + data_chunk
                    self.ble_helper.broadcast(DEVICE_LCD, message)
                    pos += 1
                    data_chunk = str(v)[pos*self.mtu:(pos+1)*self.mtu]

    def get_data(self):
        return self.ble_helper.get_data()

    def handle_action(self, state, action, params):
        if action == 'ble.scan' or (state == 'main' and action == 'BTN_BLE'):
            self.scan()
