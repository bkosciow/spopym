from service.menu import MenuItem
from service.action_interface import ActionInterface
from pprint import pprint


class Security(ActionInterface):
    storage_lock_pattern_name = 'security.lock_patter'
    storage_use_lock_name = 'security.use_lock'

    def __init__(self, config, storage):
        ActionInterface.__init__(self, config)
        self.storage = storage
        self.menu_callback = None
        self.temp_pattern = []
        self.ignore_next_click = False

    def get_menu(self):
        menu = MenuItem('Lock', options=[])
        menu.add(
            MenuItem('Set pattern', action_name="security.set_pattern", callback=self.menu_callback)
        )

        pattern = self.storage.get(self.storage_lock_pattern_name)
        pprint(pattern)
        print(type(pattern))
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

            menu.add(
                MenuItem('Lock now', action_name="security.lock_device", callback=self.menu_callback)
            )

        return [menu]

    def handle_action(self, state, action, params):
        if not self.ignore_next_click and state == 'set_pattern':
            if action == 'encoder_click':
                print("pattern=", self.temp_pattern)
                self.storage.set(self.storage_lock_pattern_name, self.temp_pattern)
                self.temp_pattern = []
                self.set_state('menu')
            else:
                print("adding action", action)
                self.temp_pattern.append(action)

        if self.ignore_next_click:
            self.ignore_next_click = False

        if action == 'security.set_pattern':
            self.set_state('set_pattern')
            self.temp_pattern = []
            self.ignore_next_click = True

        if action == 'security.enable_lock':
            self.storage.set(self.storage_use_lock_name, 1)

        if action == 'security.disable_lock':
            self.storage.set(self.storage_use_lock_name, None)

        if action == 'security.lock_device':
            pass
