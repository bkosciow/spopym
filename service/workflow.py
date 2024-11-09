import os
from scheduler.executor import Executor
from scheduler.task import Task


class Workflow:
    def __init__(self, config, lcd, menu, spotify, ble):
        self.config = config
        self.menu = menu
        self.lcd = lcd
        self.ble = ble
        self.state = 'main'
        self.spotify = spotify
        self.app_works = True
        self.executor = Executor()
        self.init_tasks()

    def init_tasks(self):
        lcd_task = Task('lcd_refresh', self.refresh_lcd)
        self.executor.every_seconds(2, lcd_task, False)
        self.executor.start()

    def refresh_lcd(self):
        if self.state == 'main':
            self.lcd.show_main()

    def shutdown(self):
        self.executor.stop()

    def menu_action(self, name, params=None):
        if params is None:
            params = []
        print("menu_action ", name, params)
        if name == 'encoder_click':
            if self.state == 'main':
                self.state = 'menu'
                self.menu.start()
            elif self.state == 'menu':
                self.menu.activate()

        if name == 'encoder_inc':
            if self.state == 'menu':
                self.menu.move_up()
            if self.state == "main":
                self.spotify.increase_volume()

        if name == 'encoder_dec':
            if self.state == 'menu':
                self.menu.move_down()
            if self.state == "main":
                self.spotify.decrease_volume()

        if name == 'close_menu' or name == 'GPIO16':
            if self.state == 'menu':
                self.state = 'main'
                self.lcd.clear()
                self.lcd.show_main()

        if name == 'lcd.show_popup':
            self.lcd.save_screen()
            self.lcd.show_popup(params['text'])

        if name == 'lcd.hide_popup':
            self.lcd.restore_screen()

        if name == 'sys.shutdown':
            self.lcd.shutdown()
            self.app_works = False
            # os.system("sudo shutdown -h now")

        if name == 'spotify.connect':
            self.lcd.show_authorize()

        if name == 'spotify.device':
            if params['device'] is None:
                self.spotify.set_device(None)
            else:
                self.spotify.set_device(params['device'])

        if name == 'ble.scan' or (self.state == 'main' and name == 'GPIO5'):
            self.ble.scan()

        if name == 'next':
            self.spotify.next_track()

        if name == 'prev':
            self.spotify.prev_track()

        if name == 'play' or (self.state == 'main' and name == 'GPIO25'):
            self.spotify.start_play()

        if name == 'stop':
            self.spotify.pause_play()
