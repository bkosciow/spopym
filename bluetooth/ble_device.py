from queue import Queue


class Device:
    def __init__(self, device, read_buffer_size=20):
        self.device = device
        self.services = {}
        self.characteristics = {}
        self.read_buffer = Queue(read_buffer_size)

    def add_service(self, s):
        self.services[s.uuid] = s

    def add_characteristic(self, c):
        self.characteristics[str(c.uuid)] = c

    def support_characteristic(self, uuid):
        return uuid in self.characteristics

    def write(self, uuid, data):
        self.characteristics[uuid].write(data)

    def append(self, data, cHandle):
        if self.read_buffer.full():
            self.read_buffer.get()
        self.read_buffer.put(data)

    def pop(self):
        return None if self.read_buffer.empty() else self.read_buffer.get()

    def read(self, uuid):
        return self.characteristics[uuid].read()