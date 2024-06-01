


class Menu:
    def __init__(self, menu, lcd):
        self.menu = menu
        self.lcd = lcd
        self.markers = {
            'not_selected': "  ",
            'selected': "> ",
            "dir": " >>",
            'not_dir': "   ",
        }
        self.level = None
        self.position = 0
        self.top_offset = 0

    def start(self):
        self.level = None
        self.position = 0
        self.draw()

    def _get_current_menu(self):
        if not self.level:
            current = self.menu
        else:
            current = self.menu[self.level[0]]

        return current

    def draw(self):

        idx = 0
        for item in self._get_current_menu():
            is_dir = self.markers['dir'] if 'options' in item else self.markers['not_dir']
            is_selected = self.markers['selected'] if idx == self.position else self.markers['not_selected']
            self.lcd.write(is_selected + item['name'] + is_dir, 0, idx + self.top_offset)
            # print(is_selected + item['name'] + is_dir)
            idx += 1

        self.lcd.flush()

    def move_up(self):
        current = self._get_current_menu()
        if self.position == 0:
            self.position = len(current)-1
        else:
            self.position -= 1

        self.draw()

    def move_down(self):
        current = self._get_current_menu()
        if self.position == len(current)-1:
            self.position = 0
        else:
            self.position += 1

        self.draw()

    def activate(self):
        print(self.position)
        print(self.level)
        current = self._get_current_menu()[self.position]
        print(current)
        if 'callback' in current and current['callback'] is not None:
            current['callback'](current['name'])
