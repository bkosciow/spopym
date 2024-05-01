import bluepy.btle as btle


def scan(length=3):
    scanner = btle.Scanner()
    devices = None

    try:
        devices = scanner.scan(length)
    except btle.BTLEDisconnectError:
        pass

    return devices
