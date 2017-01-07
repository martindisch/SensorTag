import pygatt
import time

def tempConvert(rawObjTemp, rawAmbTemp):
    SCALE_LSB = 0.03125
    t = rawObjTemp >> 2
    obj = t * SCALE_LSB
    t = rawAmbTemp >> 2
    amb = t * SCALE_LSB
    return [obj, amb]
    
def humConvert(rawTemp, rawHum):
    temp = (float(rawTemp) / 65536) * 165 - 40
    hum = (float(rawHum) / 65536) * 100
    return [temp, hum]

MAC = '24:71:89:BC:84:84'
adapter = pygatt.GATTToolBackend()

try:
    adapter.start()
    print "Connecting to " + MAC
    device = adapter.connect(MAC)
    print "Connected. Enabling sensors"
    device.char_write('f000aa02-0451-4000-b000-000000000000', bytearray([0x01]))
    device.char_write('f000aa22-0451-4000-b000-000000000000', bytearray([0x01]))
    print "Sensors enabled. Starting measurements"
    time.sleep(2)
    print "\n"
    while True:
        valueTemp = device.char_read('f000aa01-0451-4000-b000-000000000000')
        valueHum = device.char_read('f000aa21-0451-4000-b000-000000000000')
        bytes = []
        for x in valueTemp: bytes.append("{:02x}".format(x))
        rawObjTemp = int('0x' + bytes[1] + bytes[0], 16)
        rawAmbTemp = int('0x' + bytes[3] + bytes[2], 16)
        resultsTemp = tempConvert(rawObjTemp, rawAmbTemp)
        bytes = []
        for x in valueHum: bytes.append("{:02x}".format(x))
        rawTemp = int ('0x' + bytes[1] + bytes[0], 16)
        rawHum = int ('0x' + bytes[3] + bytes[2], 16)
        resultsHum = humConvert(rawTemp, rawHum)
        print "\033[3A"
        print "Obj: {:<5.1f} Amb: {:<5.1f}".format(resultsTemp[0], resultsTemp[1])
        print "Tmp: {:<5.1f} Hum: {:<5.1f}".format(resultsHum[0], resultsHum[1])
        time.sleep(1)
finally:
    adapter.stop()
