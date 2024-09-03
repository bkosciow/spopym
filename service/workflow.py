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
        spotify_default_device = Task('spotify_default_device', self.spotify.set_active_device)
        self.executor.every_seconds(3, spotify_default_device, False)

        lcd_task = Task('lcd_refresh', self.refresh_lcd)
        self.executor.every_seconds(2, lcd_task, False)
        self.executor.start()

    def control_callback(self, action):
        print("control_callback ", action)
        if action == 'encoder_click':
            if self.state == 'main':
                self.state = 'menu'
                self.menu.start()
            elif self.state == 'menu':
                self.menu.activate()

        if action == 'encoder_inc':
            if self.state == 'menu':
                self.menu.move_up()
            if self.state == "main":
                self.spotify.increase_volume()

        if action == 'encoder_dec':
            if self.state == 'menu':
                self.menu.move_down()
            if self.state == "main":
                self.spotify.decrease_volume()

        if action == 'close_menu' or action == 'GPIO16':
            if self.state == 'menu':
                self.state = 'main'
                self.lcd.clear()
                self.lcd.show_main()

    def refresh_lcd(self):
        if self.state == 'main':
            self.lcd.show_main()

    def shutdown(self):
        self.executor.stop()

    def menu_action(self, name, params=[]):
        print("menu_action ", name, params)
        if name == 'sys.shutdown':
            self.lcd.shutdown()
            self.app_works = False
            # os.system("sudo shutdown -h now")
        if name == 'spotify.connect':
            self.lcd.show_authorize()
        if name == 'spotify.device':
            self.config.set_param('spotify.device', params)
            if params['id'] is None:
                self.config.set_param('spotify.use_active', True)
                self.spotify.set_active_device()
            else:
                self.config.set_param('spotify.use_active', False)
        if name == 'ble.scan':
            self.ble.scan()
