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
        self.level = None
        self.position = 0
        self.close_event = None

    def add_menu_item(self, menu, parent=None):
        self.menu.add(menu)

    def start(self):
        self.level = []
        self.position = 0
        self.display.clear()
        self.draw()

    def _get_current_menu_item(self):
        if not self.level:
            current = self.menu
        else:
            current = None
            for i in self.level:
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

    def draw(self, clear=False):
        idx = 0
        menu_item = self._get_current_menu_item()
        menu = []
        for item in menu_item.options:
            appendix = self.markers['dir'] if item.is_dir() else self.markers['not_dir']
            is_selected = self.markers['selected'] if idx == self.position else self.markers['not_selected']
            menu.append(is_selected + item.label + appendix)
            idx += 1
        self.display.show_menu(menu, clear, self.position)

    def move_up(self):
        current = self._get_current_menu_item()
        if self.position == 0:
            self.position = len(current.options)-1
        else:
            self.position -= 1

        self.draw()

    def move_down(self):
        current = self._get_current_menu_item()
        if self.position == len(current.options)-1:
            self.position = 0
        else:
            self.position += 1

        self.draw()

    def activate(self):
        menu_item = self._get_current_menu_item()
        current = menu_item.options[self.position]
        if current.callback is not None:
            current.callback(current.action_name, current.params)
        if current.generator is not None:
            current.options = current.generator()
        if current.options is not None:
            self.level.append(self.position)
            self.position = 0
            self.draw(True)

    def back(self, action, params=[]):
        if len(self.level) == 0:
            self.close_event('close_menu')
        else:
            self.level.pop()
            self.position = 0
            self.draw(True)

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
