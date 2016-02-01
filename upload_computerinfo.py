import configparser, json # serialization
import whatpulse

CONFIG_FILE = 'whatpulsed.conf'
STATE_FILE = 'whatpulsed.json'

wp = whatpulse.Client()

# copied from whatpulsed.py
config = configparser.ConfigParser(allow_no_value=True)
with open(CONFIG_FILE, 'r') as config_file:
    config.read_file(config_file)

    try:
        with open(STATE_FILE, 'r') as state_file:
            state = json.load(state_file)

            # TODO: load more state to be sure
            wp.userid = state['login']['userid']
            wp.computerid = state['login']['computerid']
            wp.hash = state['login']['hash']
            wp.token = state['login']['token']
    except FileNotFoundError: # empty state
        wp.try_login(config['login']['email'], config['login']['password'])
        wp.login(config['login']['computer'])

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

    j['ComputerPlatform'] += '\n'

    computer_info = json.dumps(j)

if wp.client_token and computer_info:
    req = whatpulse.requests.UploadComputerinfoRequest(wp.client_token, computer_info)
    wp.s.request(req)
