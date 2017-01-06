import pygatt
import time

def tempConvert(rawObjTemp, rawAmbTemp):
    SCALE_LSB = 0.03125
    t = rawObjTemp >> 2
    resultObj = t * SCALE_LSB
    t = rawAmbTemp >> 2
    resultAmb = t * SCALE_LSB
    return [resultObj, resultAmb]

adapter = pygatt.GATTToolBackend()

try:
    adapter.start()
    device = adapter.connect('24:71:89:BC:84:84')
    device.char_write("f000aa02-0451-4000-b000-000000000000", bytearray([0x01]))
    time.sleep(2)
    while True:
        value = device.char_read('f000aa01-0451-4000-b000-000000000000')
        bytes = []
        for x in value: bytes.append("{:02x}".format(x))
        rawObjTemp = int('0x' + bytes[1] + bytes[0], 16)
        rawAmbTemp = int('0x' + bytes[3] + bytes[2], 16)
        results = tempConvert(rawObjTemp, rawAmbTemp)
        print "Obj: {:.1f} Amb: {:.1f}".format(results[0], results[1])
        time.sleep(1)
finally:
    adapter.stop()
