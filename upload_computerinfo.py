import whatpulse
import json

wp = whatpulse.Client()
wp.try_login('whattester@mailinator.com', 'whattester')
wp.login('whatpulse3')
wp.client_login()

def stringify(j):
    '''Turn all booleans and integers in JSON object into strings'''
    if isinstance(j, dict):
        j2 = {}
        for key, value in j.items():
            j2[key] = stringify(value)
        return j2
    elif isinstance(j, bool):
        return "true" if j else "false"
    elif isinstance(j, int):
        return str(j)
    else:
        return j

computer_info = None
with open('computerinfo.json') as infofile:
    j = json.load(infofile)
    j = stringify(j)

    serialize = ['TrackpadInfo', 'NetworkInfo', 'KeyboardInfo', 'MonitorInfo', 'MouseInfo']
    for key in serialize:
        j[key] = json.dumps(j[key])

    j['ComputerPlatform'] += '\n';

    computer_info = json.dumps(j)

if computer_info:
    req = whatpulse.requests.UploadComputerinfoRequest(wp.client_token, computer_info)
    wp.s.request(req)
