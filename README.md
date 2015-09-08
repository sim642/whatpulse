# whatpulsed

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
    - `k` - kilo, equal to "1000"
    - `m` - mega, equal to "1000k"
    - `g` - giga, equal to "1000m"
    - `t` - tera, equal to "1000g"
* *(size)* - base 2 magnitude units
    - `k` - kibi, equal to "1024"
    - `m` - mebi, equal to "1024k"
    - `g` - gibi, equal to "1024m"
    - `t` - tebi, equal to "1024g"
* *(time)* - time magnitude units
    - `s` - second, equal to "1"
    - `m` - minute, equal to "60s"
    - `h` - hour, equal to "60m"
    - `d` - day, equal to "24h"
    - `w` - week, equal to "7d"
    - `y` - year, equal to "52w"

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
## Setup

*TODO*
