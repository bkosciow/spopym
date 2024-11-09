
class Task(object):
    def __init__(self, name, func):
        self.name = name
        self.func = func

    def execute(self):
        return self.func()
