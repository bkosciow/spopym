

class ActionInterface:
    def __init__(self, config):
        self.config = config

    def handle_action(self, state, action, params):
        raise Exception(self.__class__.__name__ + " does not implements handle_action")

    def get_state(self):
        return self.config.get_param('state')

    def set_state(self, state):
        self.config.set_param('state', state)