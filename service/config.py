"""Config parser fle"""
from configparser import ConfigParser
from importlib import import_module
from .utils import *


class Config(object):
    """Class Config"""
    def __init__(self, file="config.ini"):
        self.file = file
        self.config = ConfigParser()
        self.config.read(file)
        self.parameters = {
            'use_message': False,
            'spotify.device': None,
            'spotify.volume.step': 5,
            'spotify.use_active': True,
            'spotify.no_device': '- - - - -',
            'spotify.last_device': None # {'id': None, 'name': '- - - - -', 'volume': 0},
        }
        self.init_message()

    def get(self, name):
        if "." in name:
            section, name = name.split(".")
        else:
            section = "global"

        val = self.config.get(section, name)
        return val if val != "" else None

    def __getitem__(self, item):
        return self.config[item]

    def get_section(self, section):
        """return section"""
        return dict(self.config.items(section))

    def get_dict(self, name):
        value = self.get(name)
        return string_to_dict(value)

    def get_param(self, name):
        return self.parameters[name]

    def set_param(self, name, value):
        self.parameters[name] = value

    def init_message(self):
        if self.get("message.node_name"):
            from iot_message.message import Message
            Message.node_name = self.get("message.node_name")
            if self.get("message.encoder"):
                encClass = getattr(import_module(self.get("message.encoder")), "Cryptor")
                params = self.get("message.encoder_params")
                if params is None:
                    encInstance = encClass()
                else:
                    params = params.split(",")
                    encInstance = encClass(*params)

                Message.add_encoder(encInstance)
            self.parameters['use_message'] = True
