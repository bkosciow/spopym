from gpiozero import RotaryEncoder, Button, LED


class Control:
    def __init__(self, config, callback=None):
        self.config = config
        self.rotor = RotaryEncoder(config.get("rotary_encoder.pin_a"), config.get("rotary_encoder.pin_b"), wrap=True, max_steps=180)
        self.rotor_btn = Button(config.get("rotary_encoder.pin_button"), pull_up=False, bounce_time=0.100)
        self.encoder_last = 0
        self.callback = callback
        self.rotor.when_rotated = self.rotate_encoder
        self.rotor_btn.when_released = self.click_encoder

        self.button_one = Button(16, pull_up=True, bounce_time=0.100)
        self.button_two = Button(20, pull_up=True, bounce_time=0.100)
        self.button_three = Button(25, pull_up=True, bounce_time=0.100)
        self.button_four = Button(5, pull_up=True, bounce_time=0.100)
        self.button_one.when_released = self.click_button
        self.button_two.when_released = self.click_button
        self.button_three.when_released = self.click_button
        self.button_four.when_released = self.click_button

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
        self.callback(str(v.pin))

    def shutdown(self):
        self.power_led.off()
