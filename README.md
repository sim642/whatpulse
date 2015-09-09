# whatpulsed

## Usage

### First run

1. Create "whatpulsed.conf":
    * Write it based on the file description below  
      or
    * Copy and modify the example
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
