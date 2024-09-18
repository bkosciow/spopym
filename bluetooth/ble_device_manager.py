import time
from .ble_device import Device
import bluepy.btle as btle
import logging
logger = logging.getLogger(__name__)


class ReadDelegate(btle.DefaultDelegate):
    def __init__(self, device):
        btle.DefaultDelegate.__init__(self)
        self.device = device

    def handleNotification(self, cHandle, data):
        self.device.append(data.decode("utf-8"), cHandle)


class DeviceManager:
    def __init__(self):
        self.devices = []
        self.services = {}
        self.aliases = {}

    def support_service(self, service, characteristics):
        self.services[service] = characteristics

    def add_alias(self, uuid, name):
        self.aliases[name] = uuid

    def add(self, device):
        self.devices.append(device)

    def count_devices(self):
        return len(self.devices)

    def exists(self, dev):
        for p in self.devices:
            if p.device.addr == dev.addr:
                return True

        return False

    def add_if_supported(self, _device):
        ok = False
        try:
            handler = btle.Peripheral(_device.addr)
            device = Device(handler)
            for service in self.services:
                try:
                    s = handler.getServiceByUUID(service)
                    device.add_service(s)
                    c = s.getCharacteristics()
                    for a in c:
                        if a.uuid in self.services[service]:
                            device.add_characteristic(a)
                            ok = True

                except btle.BTLEGattError:
                    pass

            if ok:
                handler.withDelegate(ReadDelegate(device))
                self.add(device)

        except btle.BTLEDisconnectError as e:
            pass

        return ok

    def get_notifications(self, wait=0.100):
        for p in self.devices:
            try:
                if p.device._helper:
                    p.device.waitForNotifications(wait)
                else:
                    self.remove(p)
            except btle.BTLEDisconnectError as e:
                logger.debug("Dropping device %s ", p.device.addr)
                self.remove(p)
            # except

        return self.get_data_from_devices()

    def remove(self, device):
        self.devices.remove(device)

    def get_data_from_devices(self):
        ret = {}
        for device in self.devices:
            ret[device.device.addr] = device.pop()

        return ret

    def write_to_characteristic(self, uuid, data):
        for device in self.devices:
            if device.support_characteristic(uuid):
                try:
                    device.write(uuid, data)
                except btle.BTLEException as e:
                    logger.error(e)
                    if "Helper not started" in str(e):
                        self.remove(device)


