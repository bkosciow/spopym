import os


class Workflow:
    def __init__(self, config, lcd, menu, spotify):
        self.config = config
        self.menu = menu
        self.lcd = lcd
        self.state = 'main'
        self.spotify = spotify
        self.app_works = True

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

        if action == 'encoder_dec':
            if self.state == 'menu':
                self.menu.move_down()

        if action == 'close_menu' or action == 'GPIO16':
            if self.state == 'menu':
                self.state = 'main'
                self.lcd.clear()
                self.lcd.show_main()

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
