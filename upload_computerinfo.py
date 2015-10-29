import whatpulse
import json

wp = whatpulse.Client()
wp.try_login('whattester@mailinator.com', 'whattester')
wp.login('whatpulse3')
wp.client_login()

computer_info = None
with open('computerinfo.json') as infofile:
    j = json.load(infofile)

    serialize = ['TrackpadInfo', 'NetworkInfo', 'KeyboardInfo', 'MonitorInfo', 'MouseInfo']
    for key in serialize:
        j[key] = json.dumps(j[key])

    j['ComputerPlatform'] += '\n';

    # TODO: MemoryInfo as int
    # TODO: serialized booleans as booleans

    computer_info = json.dumps(j)

if computer_info:
    req = whatpulse.requests.UploadComputerinfoRequest(wp.client_token, computer_info)
    wp.s.request(req)
