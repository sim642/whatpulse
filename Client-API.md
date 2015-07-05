# Endpoint
Whatpulse client API endpoint is https://client.whatpulse.org/v1.1/. All requests are done using `POST` method and have two form fields:
* `client_version` - client version number, e.g. `2.6.1`
* `xml` - requests in XML format as described below

*NB! Some request types may use additional form fields. Detailed descriptions under specific request types below.*

To stay under the radar, it is recommended to do all queries over HTTPS and use a legitimate `client_version`. In addition `User-Agent` header should be `WhatPulse Client <client_version>` to imitate official Whatpulse client behavior as closely as possible.

The response to the query is also in XML in the format described below.

# XML
## Requests
```xml
<?xml version="1.0" encoding="UTF-8"?>
<client>
    <requests>
        <request type="...">
            <type_os>...</type_os>
            <client_version>...</client_version>
            ...
        </request>
    </requests>
</client>
```
Each `<request>` block must come with a `type` attribute. It should also according to official client always contain two tags:
* `<type_os>` - type of operating system being used, accepted values are `windows`, `linux`, `macos`
* `<client_version>` - same as in `POST` form field

In addition, there may be more tags specific to the request type being used. Details for every type are described below.

## Responses
```xml
<?xml version='1.0' encoding='UTF-8'?>
<server>
    <responses>
        <response type="...">
            <status>...</status>
            ...
        </response>
    </responses>
</server>
```
Each `<response>` block comes with a `type` attribute. It always seems to also contain one tag:
* `<status>` - HTTP-like status code regarding the request, e.g. `200` on success, `500` on error

In addition, there may be more tags specific to the response type being used. Details for every type are described below.

# Terminology
The following section of types uses following tags repeatedly:
* `<email>` - account email, used for initial login with `trylogin`
* `<password>` - account password in plaintext
* `<passwordhash>` - hashed account password
* `<username>` - account name, only used on Whatpulse website
* `<userid>` - account id, used to get `<client_token>`
* `<computer>` - computer name, may be one from `trylogin`'s `<computers>` or a new one
* `<computerid>` - computer id, used to get `<client_token>`
* `<token>` - token to be passed when pulsing, initially returned on `login`, each `pulse` request returns the token to be used for next pulse
* `<client_token>` - temporary token identifying the client, due to short lifetime it should be requested with `client_login` right before use

# Types
The following titles are types of requests which can be made and their respective responses use the same type. Under each type additional request and response tags are described.

## testproxy
Used by the official client to test whether proxy works. Suitable request to test basic querying.

Request tags: *none*

Response tags:
* `<msg>` - status text


## trylogin
Initial login on a computer. Returns the list of already existing computers on the account.

Request tags:
* `<email>`
* `<password>`

Response tags:
* `<trylogin_result>` - status text
* `<passwordhash>`
* `<computers>` - contains single `<computer>` tags


## login
Actual login as a computer.

Request tags:
* `<email>`
* `<passwordhash>`
* `<computer>`

Response tags:
* `<email>`
* `<username>`
* `<userid>`
* `<computer>`
* `<computerid>`
* `<token>`
* `<passwordhash>`
* `<totalkeys>`, `<totalclicks>`, `<totaldownload>`, `<totalupload>`, `<totaluptime>` - account total counts
* `<rankkeys>`, `<rankclicks>`, `<rankdownload>`, `<rankupload>`, `<rankuptime>` - account global ranks
* `<premium>` - `1` if account has premium
  - `<premium_expire>` - date of account's premium expiry in `YYYY-mm-dd` format


## client_login
Quick login to get `<client_token>` to use with other requests.

Request tags:
* `<userid>`
* `<computerid>`
* `<passwordhash>`

Response tags:
* `<client_token>`


## get_password_hash
Change account password.

Request tags:
* `<client_token>`
* `<real_password>` - new password

Response tags:
* `<passwordhash>`


## get_computer_id
Returns `<computerid>` by `<computer>` name.

Request tags:
* `<userid>`
* `<computer>`

Response tags:
* `<computerid>`


## resettoken
Returns a new `<token>`.

Request tags:
* `<client_token>`

Response tags:
* `<token>`


## refresh_account_info
Returns account information.

Request tags:
* `<client_token>`

Response tags:
* `<email>`
* `<username>`
* `<computer>`
* `<totalkeys>`, `<totalclicks>`, `<totaldownload>`, `<totalupload>`, `<totaluptime>` - account total counts
* `<rankkeys>`, `<rankclicks>`, `<rankdownload>`, `<rankupload>`, `<rankuptime>` - account global ranks
* `<premium>` - `1` if account has premium
  - `<premium_expire>` - date of account's premium expiry in `YYYY-mm-dd` format


## check_premium
Checks premium status.

Request tags:
* `<client_token>`

Response tags:
* `<premium>` - `1` if account has premium
  - `<premium_expire>` - date of account's premium expiry in `YYYY-mm-dd` format


## pulse
Makes a pulse.

Request tags:
* `<client_token>`
* `<token>`
* `<keycount>`, `<clickcount>`, `<download>`, `<upload>`, `<uptime>` - counts to be pulsed

Response tags:
* `<token>`
* `<totalkeys>`, `<totalclicks>`, `<totaldownload>`, `<totalupload>`, `<totaluptime>` - account total counts
* `<rankkeys>`, `<rankclicks>`, `<rankdownload>`, `<rankupload>`, `<rankuptime>` - account global ranks


## upload_heatmap_keyboard
Premium user request to upload keyboard heatmap to website.

Request tags:
* `<client_token>`

Response tags: *none*

### Form field
`keyboard_heatmap` - serialized JSON object in the format:
```json
{
    "YYYY-mm-dd hh": {
        "key": "count",
        ...
    },
    ...
}
```
where:
* `YYYY-mm-dd hh` - timestamp of the hourly block of keycounts
  - `hh` - hour without padding, i.e. from `0` to `23`
* `key` - key code, likely from http://doc.qt.io/qt-4.8/qt.html#Key-enum
* `count` - count for key, *NB! JSON string*


## upload_heatmap_buttons
Premium user request to upload mouse button heatmap to website.

Request tags:
* `<client_token>`

Response tags: *none*

### Form field
`buttons_heatmap` - serialized JSON object in the format:
```json
{
    "YYYY-mm-dd hh": {
        "button": "count",
        ...
    },
    ...
}
```
where:
* `YYYY-mm-dd hh` - timestamp of the hourly block of button counts
  - `hh` - hour without padding, i.e. from `0` to `23`
* `button` - mouse button code, likely from http://doc.qt.io/qt-4.8/qt.html#MouseButton-enum
* `count` - count for button, *NB! JSON string*


## upload_computerinfo
Uploads computer specs to website.

Request tags:
* `<client_token>`

Response tags: *none*

### Form field
`computer_info` - JSON object in the format:
```json
{
    "VideoInfo": "NVIDIA GeForce GT 440",
    "TrackpadInfo": "{}",
    "NetworkInfo": "{\"isNetworkMonitorSupported\":{\"isNetworkMonitorSupported\":\"true\"}}",
    "CPUInfo": "Intel Core i5-2310",
    "ComputerModel": "",
    "ComputerOS": "Arch Linux",
    "ComputerPlatform": "x86_64\n",
    "KeyboardInfo": "{}",
    "MemoryInfo": "5955",
    "MonitorInfo": "{\"0\":{\"height\":\"1080\",\"id\":\"0\",\"width\":\"1920\"},\"1\":{\"height\":\"1024\",\"id\":\"1\",\"width\":\"1280\"}}",
    "MouseInfo": "{}"
}
```
where the values are:
* `VideoInfo` - GPU name
* `TrackpadInfo` - serialized JSON object in unknown format, usually `{}`
* `NetworkInfo` - serialized JSON object in the following format:

    ```json
    {
        "isNetworkMonitorSupported":
        {
            "isNetworkMonitorSupported": "true"
        },
        
        "Intel 82540EM Gigabit":
        {
            "is_wifi": "false",
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
* `ComputerPlatform` - computer platform identifier, ends with `\n`, usually `i686\n` or `x86_64\n`
* `KeyboardInfo` - serialized JSON object in unknown format, usually `{}`
* `MemoryInfo` - RAM amount in bytes
* `MonitorInfo` - serialized JSON object in the following format:

    ```json
    {
        "0":
        {
            "id": "0",
            "width": "1920",
            "height": "1080",
        },
        ...
    }
    ```
    where monitor IDs as keys have values:
    - `id` - monitor ID, same as key
    - `width` - monitor width
    - `height` - monitor height
* `MouseInfo` - serialized JSON object in unknown format, usually `{}`


# Procedure
The procedure to for requests and act like a Whatpulse client is the following:

1. `trylogin` - returns `<passwordhash>` to avoid future use of plaintext `<password>` and also list of computers
2. `login` - returns `<userid>`, `<computerid>` (required for `client_login`) and `<token>` (required for `pulse`)
3. `client_login` - returns `<client_token>` (required for `pulse`)
4. `pulse` - returns next `<token>`

After `login` the returned details can be stored and reused whenever without needing to go through the actual login procedure, so for future pulsing only steps 3. and 4. will be needed.