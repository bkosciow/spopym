

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
        self.level = []
        self.position = 0
        self.lcd.clear()
        self.draw()

    def _get_current_menu(self):
        if not self.level:
            current = self.menu
        else:
            current = None
            for i in self.level:
                if not current:
                    current = self.menu[i]['options']
                else:
                    current = current[i]['options']

        return current

    def draw(self):
        idx = 0
        for item in self._get_current_menu():
            is_dir = self.markers['dir'] if 'options' in item else self.markers['not_dir']
            is_selected = self.markers['selected'] if idx == self.position else self.markers['not_selected']
            # print(item)
            print(is_selected + item['name'] + is_dir)
            self.lcd.write(is_selected + item['name'] + is_dir, 0, idx + self.top_offset)
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
        elif 'options' in current:
            self.level.append(self.position)
            self.position = 0
            self.lcd.clear()
            self.draw()

