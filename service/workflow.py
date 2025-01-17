

class Workflow:
    def __init__(self, config, display, menu, spotify, ble, control):
        self.config = config
        self.menu = menu
        self.display = display
        self.ble = ble
        self.control = control
        self.set_state('main')
        self.spotify = spotify
        self.app_works = True

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
        if name == 'encoder_click':
            if self.get_state() == 'main':
                self.set_state('menu')
                self.menu.start()
            elif self.get_state() == 'menu':
                self.menu.activate()

        if name == 'encoder_inc':
            if self.get_state() == 'menu':
                self.menu.move_up()
            if self.get_state() == "main":
                self.spotify.increase_volume()

        if name == 'encoder_dec':
            if self.get_state() == 'menu':
                self.menu.move_down()
            if self.get_state() == "main":
                self.spotify.decrease_volume()

        if name == 'close_menu' or name == 'BTN_HOME':
            if self.get_state() == 'menu':
                self.set_state('main')
                self.display.clear()
                self.display.show_main()

        if name == 'BTN_BACK' and self.get_state() == 'menu':
            self.menu.back('back')

        if name == 'lcd.show_popup':
            self.display.show_popup(
                text=params['text'],
                close_delay=params['close_delay'] if 'close_delay' in params else None
            )

        if name == 'lcd.hide_popup':
            self.display.hide_popup()

        if name == 'sys.shutdown':
            self.display.shutdown()
            self.app_works = False
            # os.system("sudo shutdown -h now")

        if name == 'spotify.connect':
            self.display.show_authorize()

        if name == 'spotify.device':
            if params['device'] is None:
                self.spotify.set_device(None)
            else:
                self.spotify.set_device(params['device'])

        if name == 'ble.scan' or (self.get_state() == 'main' and name == 'BTN_BLE'):
            self.ble.scan()

        if name == 'next':
            self.spotify.next_track()

        if name == 'prev':
            self.spotify.prev_track()

        if name == 'play' or (self.get_state() == 'main' and name == 'BTN_B'):
            self.spotify.start_play()

        if name == 'stop':
            self.spotify.pause_play()

        if name == 'shuffle':
            self.spotify.shuffle_toggle()

        if name == 'enable_led':
            self.control.enable_led(params['name'])

        if name == 'disable_led':
            self.control.disable_led(params['name'])