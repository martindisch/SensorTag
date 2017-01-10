import pygatt
import time

def tempConvert(rawTemp):
    SCALE_LSB = 0.03125
    # mask to fill in leading ones after bitshift if number is negative
    mask = 0xc000 if rawTemp > 0x7fff else 0x0000
    # right-shift by two and fill in leading ones if necessary
    t = rawTemp >> 2 | mask
    # convert to negative number if necessary
    if t > 0x7fff:
        t = -(t ^ 0xffff) + 1
    temp = t * SCALE_LSB
    return temp

def humConvert(rawTemp, rawHum):
    temp = (float(rawTemp) / 65536) * 165 - 40
    hum = (float(rawHum) / 65536) * 100
    return [temp, hum]

def dateTime():
    return time.strftime("%Y/%m/%d %H:%M:%S")

def toCSV(list):
    line = ""
    for item in list:
        line += str(item) + ","
    return line[:-1] + "\n"

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
        objTemp = tempConvert(rawObjTemp)
        ambTemp = tempConvert(rawAmbTemp)
        bytes = []
        for x in valueHum: bytes.append("{:02x}".format(x))
        rawTemp = int ('0x' + bytes[1] + bytes[0], 16)
        rawHum = int ('0x' + bytes[3] + bytes[2], 16)
        resultsHum = humConvert(rawTemp, rawHum)
        
        # console output
        print "\033[3A"
        print "Obj: {:<5.1f} Amb: {:<5.1f}".format(objTemp, ambTemp)
        print "Tmp: {:<5.1f} Hum: {:<5.1f}".format(resultsHum[0], resultsHum[1])
        
        # prepare latest data
        temp = ambTemp
        latest = [
            dateTime(), round(temp, 2), round(resultsHum[1], 2)
        ]
        
        # dump in latest
        with open("latest.csv", 'w') as f:
            f.write(toCSV(latest))
        
        # dump in history
        with open("history.csv", 'a') as f:
            f.write(toCSV(latest))
        
        time.sleep(60)
finally:
    adapter.stop()
