
class TextScroll:
    def __init__(self, text, width):
        self.width = width
        self.text = text
        self.pos = 0
        self.tick = 1

    def get_tick(self):
        if len(self.text) > self.width:
            text = self.text
            text += " * "
            text = text[self.pos:self.pos + self.width]
            self.pos += 1
            if self.pos > len(self.text):
                self.pos = 0
            if len(text) < self.width:
                text += self.text[0:self.width - len(text)]

            return text

        return self.text + " "*(self.width - len(self.text))

    def set_text(self, text):
        if text != self.text:
            self.text = text
            self.pos = 0
