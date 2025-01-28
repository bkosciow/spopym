from service.menu import MenuItem


class Security:
    def __init__(self, config, storage):
        self.config = config
        self.storage = storage
        self.menu_callback = None

    def get_menu(self):
        menu = MenuItem('Lock', options=[])
        menu.add(
            MenuItem('Set pattern', action_name="security.set_pattern", callback=self.menu_callback)
        )

        lock = self.storage.get("use_lock")
        if lock == 1:
            menu.add(
                MenuItem('Lock +', action_name="security.toggle_lock", callback=self.menu_callback)
            )
        else:
            menu.add(
                MenuItem('Lock -', action_name="security.toggle_lock", callback=self.menu_callback)
            )

        menu.add(
            MenuItem('Lock now', action_name="security.lock_device", callback=self.menu_callback)
        )

        return [menu]
