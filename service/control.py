from gpiozero import RotaryEncoder, Button, LED


class Control:
    def __init__(self, config, action_callback=None):
        self.config = config
        self.callback = action_callback
        self.rotor = RotaryEncoder(config.get("rotary_encoder.pin_a"), config.get("rotary_encoder.pin_b"), wrap=True, max_steps=180)
        self.rotor_btn = Button(config.get("rotary_encoder.pin_button"), pull_up=False, bounce_time=0.100)
        self.encoder_last = 0
        self.rotor.when_rotated = self.rotate_encoder
        self.rotor_btn.when_released = self.click_encoder
        self.button_mapper = {}

        for item in self.config.get_section('buttons'):
            if item.startswith('btn_'):
                pin = self.config.get("""buttons.%s""" % item)
                if pin:
                    button = Button(pin, pull_up=True, bounce_time=0.100)
                    button.when_released = self.click_button
                    self.button_mapper[button.pin.number] = item.upper()

        self.power_led = LED(4)
        self.power_led.on()

    def rotate_encoder(self):
        if self.encoder_last < self.rotor.steps:
            self.callback('encoder_dec')
        else:
            self.callback('encoder_inc')
        self.encoder_last = self.rotor.steps

    def click_encoder(self):
        self.callback('encoder_click')

    def click_button(self, v):
        # print(self.button_mapper[v.pin.number])
        self.callback(self.button_mapper[v.pin.number])

    def shutdown(self):
        self.power_led.off()
