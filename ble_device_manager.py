import bluepy.btle as btle
from queue import Queue


class ReadDelegate(btle.DefaultDelegate):
    def __init__(self, device):
        btle.DefaultDelegate.__init__(self)
        self.device = device

    def handleNotification(self, cHandle, data):
        self.device.append(data.decode("utf-8"), cHandle)
        # print(cHandle, " >> ", data.decode("utf-8"))


class Device:
    def __init__(self, device, read_buffer_size=20):
        self.device = device
        self.services = {}
        self.characteristics = {}
        self.read_buffor = Queue(read_buffer_size)

    def add_service(self, s):
        self.services[s.uuid] =s

    def add_characteristic(self, c):
        self.characteristics[str(c.uuid)] = c

    def support_characteristic(self, uuid):
        return uuid in self.characteristics

    def write(self, uuid, data):
        self.characteristics[uuid].write(data)

    def append(self, data, cHandle):
        if self.read_buffor.full():
            self.read_buffor.get()
        self.read_buffor.put(data)

    def read(self, uuid):
        return self.characteristics[uuid].read()


class DeviceManager:
    def __init__(self):
        """ service_uuid, (char1_uui, char2_uuid)"""
        self.devices = []
        self.services = {}
        self.mapping = {}

    def support_service(self, service, characteristics):
        self.services[service] = characteristics

    def add_mapping(self, uuid, name):
        self.mapping[name] = uuid

    def add(self, device):
        self.devices.append(device)

    def add_if_supported(self, device):
        ok = False
        try:
            handler = btle.Peripheral(device.addr)
            _device = Device(handler)
            for service in self.services:
                try:
                    s = handler.getServiceByUUID(service)
                    _device.add_service(s)
                    c = s.getCharacteristics()
                    for a in c:
                        if a.uuid in self.services[service]:
                            _device.add_characteristic(a)
                            ok = True

                except btle.BTLEGattError:
                    pass

            if ok:
                handler.withDelegate(ReadDelegate(_device))
                self.add(_device)

        except btle.BTLEDisconnectError as e:
            pass

        return ok

    def remove(self, device):
        self.devices.remove(device)

    def get_data_from_devices(self):
        for device in self.devices:
            print(device.device.addr, device.read_buffor.get())

    def write_to_characteristic(self, uuid, data):
        for device in self.devices:
            if device.support_characteristic(uuid):
                device.write(uuid, data)
