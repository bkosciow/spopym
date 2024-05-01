import bluepy.btle as btle

SCAN_TIME = 10
scanner = btle.Scanner()
devices = scanner.scan(SCAN_TIME)

for dev in devices:
    print("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
    for (adtype, desc, value) in dev.getScanData():
        print("[%d]  %s = %s" % (adtype, desc, value))

    if dev.addrType != "random":
        try:
            p = btle.Peripheral(dev.addr)
            services = p.getServices()
            for item in services:
                print(item)
        except btle.BTLEDisconnectError as e:
            print("No services")
