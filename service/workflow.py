from service.action_interface import ActionInterface


class Workflow:
    def __init__(self, config): #, display, menu, spotify, ble, control):
        self.config = config
        self.set_state('main')
        self.app_works = True
        self.handlers = []

    def add_handler(self, handler):
        if not isinstance(handler, ActionInterface):
            raise Exception("Handler " + handler.__class__.__name__ + " should extend ActionInterface")
        self.handlers.append(handler)

    def get_state(self):
        return self.config.get_param('state')

    def set_state(self, state):
        self.config.set_param('state', state)

    def shutdown(self):
        self.app_works = False
        self.menu_action('disable_led', {'name': 'LED_POWER'})
        self.menu_action('disable_led', {'name': 'LED_BLE'})

    def menu_action(self, name, params=None):
        if params is None:
            params = []
        print("menu_action ", name, params)
        for handler in self.handlers:
            if handler.handle_action(self.get_state(), name, params) is True:
                break

        if name == 'sys.shutdown':
            self.app_works = False
            # os.system("sudo shutdown -h now")
