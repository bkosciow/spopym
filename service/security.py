from service.menu import MenuItem
from service.action_interface import ActionInterface


class Security(ActionInterface):
    storage_lock_pattern_name = 'security.lock_patter'
    storage_use_lock_name = 'security.use_lock'

    def __init__(self, config, storage):
        ActionInterface.__init__(self, config)
        self.storage = storage
        self.menu_callback = None
        self.temp_pattern = []
        self.last_clicks = []

    def get_menu(self):
        menu = MenuItem('Lock', options=[])
        menu.add(
            MenuItem('Set pattern', action_name="security.set_pattern", callback=self.menu_callback)
        )

        pattern = self.storage.get(self.storage_lock_pattern_name)
        if pattern is not None:
            lock = self.storage.get(self.storage_use_lock_name)
            if lock == 1:
                menu.add(
                    MenuItem('Lock on->off', action_name="security.disable_lock", callback=self.menu_callback)
                )
            else:
                menu.add(
                    MenuItem('Lock off->on', action_name="security.enable_lock", callback=self.menu_callback)
                )

        return [menu]

    def handle_action(self, state, action, params):
        if state == 'device.locked':
            self.last_clicks.append(action)
            pattern = self.storage.get(self.storage_lock_pattern_name)

            if len(self.last_clicks) > len(pattern):
                self.last_clicks.pop(0)

            if pattern == self.last_clicks:
                self.set_state('main')
                return

        if state == 'device.locked':
            return

        if state == 'set_pattern':
            if action == 'encoder_click':
                self.storage.set(self.storage_lock_pattern_name, self.temp_pattern)
                self.temp_pattern = []
                self.config.set_param('last_button', '')
                self.set_state('menu')
            else:
                self.config.set_param('last_button', action)
                self.temp_pattern.append(action)

        if action == 'security.set_pattern':
            self.set_state('set_pattern')
            self.config.set_param('last_button', '')
            self.temp_pattern = []

        if action == 'security.enable_lock':
            self.storage.set(self.storage_use_lock_name, 1)

        if action == 'security.disable_lock':
            self.storage.set(self.storage_use_lock_name, None)

        if state == 'main' and (action == 'security.lock_device' or action == 'BTN_LOCK') and self.storage.get(self.storage_use_lock_name) == 1:
            self.last_clicks = []
            self.set_state('device.locked')
