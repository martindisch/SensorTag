# SensorTag
Some code I wrote while testing the Texas Instruments CC2650STK SensorTag.

**Disclaimer:** I'm running SensorTag firmware 1.32, it may not work with other versions.

## Components
### C programs
`util/tempconvert.c` and `util/humconvert.c` are two small programs that convert the output you would get by manually reading the data characteristics of the temperature and humidity sensor using `gatttool`. They are used by passing the output like `./tempconvert.c e0 08 48 0c`, where the output is in the format `Object[0:7] Object[8:15] Ambience[0:7] Ambience[8:15]`.

### Python data reader
`util/readdata.py` is a small Python script that connects to the SensorTag with the hardcoded MAC address and continuously displays the data from the temperature and humidity sensor.

### Weather station
This functionality consists of 3 parts.
#### logger
`server/logger.py` connects to the SensorTag using the MAC address stored in `server/mac.txt`. This is such that the address is untracked by any VCS in case the device is often changed. So be sure to have the MAC address of your SensorTag in the file, otherwise it won't work. It then reads temperature and humidity data from the SensorTag in the hardcoded interval (default 1 minute), stores the latest data in `latest.csv` and appends it to `history.csv`.

It also has the option to send you a notification on Telegram, if you have a Telegram bot. To use this feature, create the file `server/telegram.txt` and have your bot's token on the first line, and your `chat_id` on the second line. Obtaining your id is a bit difficult, see [this answer](http://stackoverflow.com/a/31081941) for more information. If you have set it up correctly, it will send you a message using the given bot after 20 connection retries have failed.

#### server
`server/server.py` listens for incoming GET requests on default port 8081. On receiving `/latest`, it returns the latest measurements from `server/latest.csv` encoded as JSON. On receiving `/history`, it returns all the historical data from `server/history.csv`.

Both the logger and server can be started by using `server/start.sh`, which creates a GNU screen session for each of them. This has the additional advantage of automatically attempting to reconnect to the SensorTag if the logger has exited due to losing the BLE connection. Please not that you'll obviously have to have GNU screen installed, as well as a working Bluetooth stack. As far as python modules go, you'll need to use pip to install web.py, pygatt and pexpect.

#### Android app
`android/Weather` is an Android app using the service provided by the server to get and display current and historical data. The IP and port of the server are stored in the untracked string value file `creds.xml` as the string `R.string.IP` in order not to show up in VCS.

## Libraries
This project uses the following libraries
* [pygatt](https://github.com/peplin/pygatt)
* [android-async-http](https://github.com/loopj/android-async-http)
* [MPAndroidChart](https://github.com/PhilJay/MPAndroidChart)
* Android AppCompat and Support Library

## License
[MIT license](LICENSE)
