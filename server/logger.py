import pygatt
import time
import os.path
import requests

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
    
def tail(f, window=20):
    """
    Returns the last `window` lines of file `f` as a list.
    """
    if window == 0:
        return []
    BUFSIZ = 1024
    f.seek(0, 2)
    bytes = f.tell()
    size = window + 1
    block = -1
    data = []
    while size > 0 and bytes > 0:
        if bytes - BUFSIZ > 0:
            # Seek back one whole BUFSIZ
            f.seek(block * BUFSIZ, 2)
            # read BUFFER
            data.insert(0, f.read(BUFSIZ))
        else:
            # file too small, start from begining
            f.seek(0,0)
            # only read what was not read
            data.insert(0, f.read(bytes))
        linesFound = data[0].count('\n')
        size -= linesFound
        bytes -= BUFSIZ
        block -= 1
    return ''.join(data).splitlines()[-window:]
    
def detect(cons_max):
    hum = -1
    count = 0
    with open("history.csv", 'r') as f:
        lines = tail(f, cons_max * 2)
    occ = 0
    for line in lines:
        current = float(line.split(",")[2])
        if current == hum and current < 97:
            count += 1
        else:
            # process previous
            if count >= cons_max:
                occ = max(count, cons_max)
            # reset
            hum = current
            count = 0
    return occ

# prepare Telegram data
hasTelegram = False
if os.path.isfile("telegram.txt"):
    with open("telegram.txt", 'r') as f:
        lines = f.readlines()
        token = lines[0].strip()
        ownerId = lines[1].strip()
        url = 'https://api.telegram.org/bot%s/' % token
        hasTelegram = True

with open("mac.txt", 'r') as f:
    MAC = f.readlines()[0].strip("\n")
adapter = pygatt.GATTToolBackend()

# the number of consecutive humidity values that are critical if they're equal
cons_max = 90
# the counter for regular check of the last cons_max*2 humidity values
cons_count = 0

try:
    adapter.start()
    print dateTime() + " - Connecting to " + MAC
    device = adapter.connect(MAC)
    print "Connected. Enabling sensors"
    device.char_write('f000aa02-0451-4000-b000-000000000000', bytearray([0x01]))
    device.char_write('f000aa22-0451-4000-b000-000000000000', bytearray([0x01]))
    print "Sensors enabled. Starting measurements"
    time.sleep(2)
    print "\n"
    # initialize variable to store last valid humidity reading
    lastHum = -1
    # attempt to load previous humidity reading
    if os.path.isfile("latest.csv"):
        with open("latest.csv", 'r') as f:
            timeTempHum = f.readlines()[0].strip("\n").split(",")
            lastHum = timeTempHum[2]
            
    # since we're connected, reset retry counter
    with open("retry.txt", 'w') as f:
        f.write("0")
    
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
        humidity = resultsHum[1]
        # check if we have an erroneous humidity reading
        if lastHum > -1 and humidity > 99:
            humidity = lastHum
        lastHum = humidity
        latest = [
            dateTime(), format(temp, ".2f"), format(float(humidity), ".2f")
        ]
        
        # dump in latest
        with open("latest.csv", 'w') as f:
            f.write(toCSV(latest))
        
        # dump in history
        with open("history.csv", 'a') as f:
            f.write(toCSV(latest))
            
        cons_count += 1
        if cons_count == cons_max:
            # check last cons_max*2 humidity values
            cons_num = detect(cons_max)
            # send message
            if cons_num > 0 and hasTelegram:
                message = ("%d consecutive humidity values.\n" % cons_num +
                           "Battery may be low.")
                requests.post(
                    url + 'sendMessage',
                    params = dict(chat_id=ownerId, text=message))
            # reset counter
            cons_count = 0
        
        time.sleep(60)
finally:
    # attempt to load retry count if it exists
    if os.path.isfile("retry.txt"):
        with open("retry.txt", 'r') as f:
            retries = int(f.readlines()[0].strip())
    else:
        retries = 0
        
    # notify user after some retries
    if retries == 20 and hasTelegram:
        message = "SensorTag is unreachable after 20 retries"
        requests.post(
            url + 'sendMessage',
            params = dict(chat_id=ownerId, text=message))
            
    # don't let retry counter go over a certain limit
    if retries > 999: retries = 999
        
    # write incremented retry count
    with open("retry.txt", 'w') as f:
        f.write(str(retries + 1))
        
    # stop pygatt adapter
    adapter.stop()
