from gpiozero import RotaryEncoder, Button


class Control:
    def __init__(self, callback=None):
        self.rotor = RotaryEncoder(19, 26, wrap=True, max_steps=180)
        self.rotor_btn = Button(21, pull_up=False)
        self.encoder_last = 0
        self.callback = callback
        self.rotor.when_rotated = self.rotate_encoder
        self.rotor_btn.when_released = self.click_encoder

    def rotate_encoder(self):
        if self.encoder_last < self.rotor.steps:
            self.callback('encoder_dec')
        else:
            self.callback('encoder_inc')
        self.encoder_last = self.rotor.steps

    def click_encoder(self):
        self.callback('encoder_click')
