# whatpulse

*WhatPulse reverse engineered*

This project consists of three parts:

1. Reverse engineering **WhatPulse Client API** protocol.

   The reverse engineering has been done using [mitmproxy](https://mitmproxy.org/). The captures can be found in [caps](caps) directory. All results have been thoroughly documented in [API.md](API.md).

2. Implementing the protocol as a **Python library**.

   The implementation of the protocol in Python 3 can be found in [whatpulse](whatpulse) directory.

3. Making a **replacement client** for WhatPulse using the library.

   The replacement client is called [whatpulsed](#whatpulsed). An additional tool [upload_computerinfo](#upload_computerinfo) comes with it. Both are described below in more detail.


# whatpulsed

This program is a replacement for WhatPulse client: it counts keys, clicks; measures download, upload, uptime and pulses that information manually or automatically. The idea is to provide pulsing features similar to the official client in a lightweight form, without the GUI and fancy visual statistics. Since whatpulsed is coded in Python 3 it can be run on platforms unsupported by the official client, e.g. headless systems and other architectures (e.g. ARM on Raspberry Pi). Currently it only works on Linux.

## Dependencies
* [python-daemon](https://pypi.python.org/pypi/python-daemon/) - used for running in the background

  Install with
  ```
  sudo pip3 install python-daemon
  ```
  
* [python-evdev](https://python-evdev.readthedocs.org/en/latest/) - used for parsing input from `/dev/input/event*`

  Install with
  ```
  sudo pip3 install evdev
  ```

* [lxml](http://lxml.de/) - used for communicating with the XML API

  Install with
  ```
  sudo apt-get install libxml2-dev libxslt1-dev
  sudo pip3 install lxml
  ```
  or
  ```
  sudo apt-get install python3-lxml
  ```

## Usage

### First run

1. Create "whatpulsed.conf":
    * Write it based on the [file description below](#whatpulsedconf)  
      or
    * Copy and modify [the example](whatpulsed.conf)
2. Run with `python3 whatpulsed.py`
3. Wait for "whatpulsed.json" to be created
4. *(optional)* Remove plaintext login details from "whatpulsed.conf" by deleting `login` section

### Future runs

1. Run with `python3 whatpulsed.py`
2. Manually pulse by sending the process a `SIGUSR1`
3. Gracefully stop whatpulsed by sending the process a `SIGTERM`

## Files

### whatpulsed.conf

This is the configuration file for whatpulsed. It is in **INI format** and has the following sections:

* `login` - WhatPulse login details (optional, only required when no state file "whatpulsed.json" exists)
    - `email` - WhatPulse login email
    - `password` - WhatPulse login password
    - `computer` - computer name to log into
* `state` - state options (optional, but recommended)
    - `interval` *(time)* - state saving interval
* `interfaces` - network interfaces
    - list of interfaces to measure (no INI values), e.g. `eth0`
* `inputs` - evdev inputs
    - list of input devices to count (no INI values), e.g. `/dev/input/event2`
* `pulse` - automatic pulsing conditions (any satisfied condition pulses)
    - `keys` *(general)* - key count to pulse on
    - `clicks` *(general)* - click count to pulse on
    - `download` *(size)* - download amount to pulse on
    - `upload` *(size)* - upload amount to pulse on
    - `uptime` *(time)* - uptime to pulse on

#### converter

Some values can be in converted format, allowing more human-readable values:
* *(general)* - generic magnitude units

    | unit | meaning | value |
    | ---- | ------- | ----- |
    | k    | kilo    | 1000  |
    | m    | mega    | 1000k |
    | g    | giga    | 1000m |
    | t    | tera    | 1000g |
    e.g. `1m500k` means "1.5 million"
* *(size)* - base 2 magnitude units

    | unit | meaning | value |
    | ---- | ------- | ----- |
    | k    | kibi    | 1024  |
    | m    | mebi    | 1024k |
    | g    | gibi    | 1024m |
    | t    | tebi    | 1024g |
    e.g. `1g500m` means "1.5 gigabytes"
* *(time)* - time magnitude units

    | unit | meaning | value |
    | ---- | ------- | ----- |
    | s    | second  | 1     |
    | m    | minute  | 60s   |
    | h    | hour    | 60m   |
    | d    | day     | 24h   |
    | w    | week    | 7d    |
    | y    | year    | 52w   |
    e.g. `3d7h10m` means "3 days, 7 hours and 10 minutes"

### whatpulsed.json

This is the state file for whatpulsed and is not meant to be directly manipulated. It is in **JSON format** and is structured as follows:
* `login` - logged in state
    - `userid`
    - `computerid`
    - `hash`
    - `token`
* `stats` - unpulsed stats
    - `keys`
    - `clicks`
    - `download`
    - `upload`
    - `upime`

# upload_computerinfo

This program allows uploading computer information (specs) to WhatPulse website for others to see without needing to install the official client. It allows manually specifying all supported information and uploading it via this simple script.

## Usage

1. Provide WhatPulse login details:
    1. Have "whatpulsed.json" as the [result of running whatpulsed](#first-run)  
       or
    2. Create "whatpulsed.conf" as [described above](#whatpulsedconf) (only `login` section is required)
2. Create "computerinfo.json":
    * Write it based on the [file description below](#computerinfojson)  
      or
    * Copy and modify [the example](computerinfo.json)
3. Run with `python3 upload_computerinfo.py`

## Files

### computerinfo.json

This is the computer info file for upload_computerinfo. It is in **JSON format** and is structured similarly to the JSON object used for [upload_computerinfo request in the API](API.md#upload_computerinfo):
```json
{
    "VideoInfo": "NVIDIA GeForce GT 440",
    "TrackpadInfo": {},
    "NetworkInfo":
    {
        "isNetworkMonitorSupported":
        {
            "isNetworkMonitorSupported": true
        }
    },
    "CPUInfo": "Intel Core i5-2310",
    "ComputerModel": "",
    "ComputerOS": "Arch Linux",
    "ComputerPlatform": "x86_64",
    "KeyboardInfo": {},
    "MemoryInfo": 5955,
    "MonitorInfo":
    {
        "0":
        {
            "id": 0,
            "width": 1920,
            "height": 1080,
        },
        "1":
        {
            "id": 1,
            "width": 1280,
            "height": 1024,
        }
    },
    "MouseInfo": {}
}
```
where the values are:
* `VideoInfo` - GPU name
* `TrackpadInfo` - JSON object in unknown format, usually `{}`
* `NetworkInfo` - JSON object in the following format:

    ```json
    {
        "isNetworkMonitorSupported":
        {
            "isNetworkMonitorSupported": true
        },

        "Intel 82540EM Gigabit":
        {
            "is_wifi": false,
            "description": "Intel 82540EM Gigabit"
        },
        ...
    }
    ```
    where network cards as keys have values:
    - `is_wifi` - network card Wi-Fi ability
    - `description` - network card name, same as key
* `CPUInfo` - CPU name
* `ComputerModel` - computer model name, usually empty
* `ComputerOS` - operating system name
* `ComputerPlatform` - computer platform identifier, usually `i686` or `x86_64`
* `KeyboardInfo` - JSON object in unknown format, usually `{}`
* `MemoryInfo` - RAM amount in megabytes
* `MonitorInfo` - JSON object in the following format:

    ```json
    {
        "0":
        {
            "id": 0,
            "width": 1920,
            "height": 1080,
        },
        ...
    }
    ```
    where monitor IDs as keys have values:
    - `id` - monitor ID, same as key
    - `width` - monitor width
    - `height` - monitor height
* `MouseInfo` - JSON object in unknown format, usually `{}`
