from service.action_interface import ActionInterface


class MenuItem:
    def __init__(self, label, action_name=None, callback=None,
                 options=None, generator=None, params=None):
        self.label = label
        self.action_name = action_name
        self.callback = callback
        self.generator = generator
        self.options = options
        self.params = params

    def add(self, menu_item):
        self.options.append(menu_item)

    def is_dir(self):
        return self.options is not None or self.generator is not None


class Menu(ActionInterface):
    def __init__(self, config, display):
        ActionInterface.__init__(self, config)
        self.menu = MenuItem("root", options=[])
        self.display = display
        self.markers = {
            'not_selected': "  ",
            'selected': "> ",
            "dir": " >>",
            'not_dir': "   ",
            'back': ' <back> ',
        }
        self.config.set_param("menu.level", None)
        self.config.set_param("menu.position", 0)
        self.close_event = None

    def add_menu_item(self, menu, parent=None):
        self.menu.add(menu)

    def start(self):
        self.config.set_param("menu.level", [])
        self.config.set_param("menu.position", 0)
        self.display.clear()
        self.generate_menu()

    def _get_current_menu_item(self):
        if not self.config.get_param("menu.level"):
            current = self.menu
        else:
            current = None
            for i in self.config.get_param("menu.level"):
                if not current:
                    current = self.menu.options[i]
                else:
                    current = current.options[i]
        has_back = False
        for item in current.options:
            if 'back' == item.action_name:
                has_back = True

        if not has_back:
            current.add(
                MenuItem(label=self.markers['back'], action_name='back', callback=self.back)
            )

        return current

    def generate_menu(self):
        idx = 0
        menu_item = self._get_current_menu_item()
        menu = []
        for item in menu_item.options:
            appendix = self.markers['dir'] if item.is_dir() else self.markers['not_dir']
            is_selected = self.markers['selected'] if idx == self.config.get_param("menu.position") else self.markers['not_selected']
            menu.append(is_selected + item.label + appendix)
            idx += 1
        self.config.set_param("menu.menu", menu)

    def move_up(self):
        current = self._get_current_menu_item()
        if self.config.get_param("menu.position") == 0:
            self.config.set_param("menu.position", len(current.options) - 1)
        else:
            self.config.set_param("menu.position", self.config.get_param("menu.position")-1)

        self.generate_menu()

    def move_down(self):
        current = self._get_current_menu_item()
        if self.config.get_param("menu.position") == len(current.options)-1:
            self.config.set_param("menu.position", 0)
        else:
            self.config.set_param("menu.position", self.config.get_param("menu.position")+1)

        self.generate_menu()

    def activate(self):
        menu_item = self._get_current_menu_item()
        current = menu_item.options[self.config.get_param("menu.position")]
        if current.callback is not None:
            current.callback(current.action_name, current.params)
        if current.generator is not None:
            current.options = current.generator()
        if current.options is not None:
            self.config.get_param("menu.level").append(self.config.get_param("menu.position"))
            self.config.set_param("menu.position", 0)
            self.generate_menu()

    def back(self, action, params=[]):
        if len(self.config.get_param("menu.level")) == 0:
            self.close_event('close_menu')
        else:
            self.config.get_param("menu.level").pop()
            self.config.set_param("menu.position", 0)
            self.generate_menu()

    def handle_action(self, state, action, params):
        if action == 'encoder_click':
            if state == 'main':
                self.set_state('menu')
                self.start()
            elif state == 'menu':
                self.activate()
                return True

        if action == 'encoder_inc' and state == 'menu':
            self.move_up()

        if action == 'encoder_dec' and state == 'menu':
            self.move_down()

        if action == 'BTN_BACK' and state == 'menu':
            self.back('back')
