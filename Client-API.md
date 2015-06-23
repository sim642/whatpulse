# Endpoint
Whatpulse client API endpoint is https://client.whatpulse.org/v1.1/. All requests are done using `POST` method and have two form fields:
* `client_version` - contains client version number, e.g. `2.6.1`
* `xml` - contains requests in XML format as described below

To stay under the radar, it is recommended to do all queries over HTTPS and use a legitimate `client_version`. In addition `User-Agent` header should be `WhatPulse Client <client_version>` to imitate official Whatpulse client behavior as closely as possible.

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
* `<type_os>` - contains the type of operating system being used, accepted values are `windows`, `linux`, `macos`
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
* `<status>` - contains HTTP-like status code regarding the request, e.g. `200` on success, `500` on error

In addition, there may be more tags specific to the response type being used. Details for every type are described below.