# Endpoint
Whatpulse client API endpoint is https://client.whatpulse.org/v1.1/. All requests are done using `POST` method and have two form fields:
* `client_version` - contains client version number, e.g. `2.6.1`
* `xml` - contains requests in XML format as described below

To stay under the radar, it is recommended to do all queries over HTTPS and use a legitimate `client_version`. In addition `User-Agent` header should be `WhatPulse Client <client_version>` to imitate official Whatpulse client behavior as closely as possible.