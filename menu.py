

class Menu:
    def __init__(self, menu, lcd):
        self.menu = menu
        self.lcd = lcd
        self.markers = {
            'not_selected': "  ",
            'selected': "> ",
            "dir": " >>",
            'not_dir': "   ",
            'back': ' <back> ',
        }
        self.level = None
        self.position = 0
        self.top_offset = 1
        self.close_event = None

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

        has_back = False
        for item in current:
            if self.markers['back'] == item['name']:
                has_back = True
        if not has_back:
            current.append({
                'name': self.markers['back'],
                'callback': self.back
            })

        return current

    def draw(self):
        idx = 0
        for item in self._get_current_menu():
            is_dir = self.markers['dir'] if 'options' in item or 'generator' in item else self.markers['not_dir']
            is_selected = self.markers['selected'] if idx == self.position else self.markers['not_selected']
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
        current = self._get_current_menu()[self.position]
        if 'callback' in current and current['callback'] is not None:
            current['callback'](current['name'])
        elif 'generator' in current:
            # current['options'] = []
            current['options'] = current['generator']()
            self.level.append(self.position)
            self.position = 0
            self.lcd.clear()
            self.draw()
        elif 'options' in current:
            self.level.append(self.position)
            self.position = 0
            self.lcd.clear()
            self.draw()

    def back(self, action):
        if len(self.level) == 0:
            self.close_event('close_menu')
        else:
            self.level.pop()
            self.position = 0
            self.lcd.clear()
            self.draw()

