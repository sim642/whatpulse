import daemon, signal
import configparser, whatpulse
from evdev import InputDevice, KeyEvent, ecodes
import selectors
import time
import converter
import requests
import json
import sys
import lockfile

CONFIG_FILE = 'whatpulsed.conf'
STATE_FILE = 'whatpulsed.json'
LOCK_FILE = 'whatpulsed.pid'

BYTE_BASE = 1024

stdout_file = open('stdout.log', 'w+')
stderr_file = open('stderr.log', 'w+')

config = configparser.ConfigParser(allow_no_value=True)

inputs = []
interfaces = []

selector = None
wp = whatpulse.Client()

keys = None
clicks = None
total_bytes = None
prev_bytes = None
total_time = None
prev_time = None

prev_save = None

def reset_stats():
	global keys, clicks, total_bytes, total_time
	keys = 0
	clicks = 0
	total_bytes = {'rx': 0, 'tx': 0}
	total_time = 0

def setup():
	global inputs, interfaces, keys, clicks, total_bytes, total_time
	config_file = open(CONFIG_FILE, 'r')
	config.read_file(config_file)

	reset_stats()

	try:
		state_file = open(STATE_FILE, 'r')
		state = json.load(state_file)

		# TODO: load more state to be sure
		wp.userid = state['login']['userid']
		wp.computerid = state['login']['computerid']
		wp.hash = state['login']['hash']
		wp.token = state['login']['token']

		wp.client_login()
		wp.refresh()

		keys = state['stats']['keys']
		clicks = state['stats']['clicks']
		total_bytes['rx'] = state['stats']['download']
		total_bytes['tx'] = state['stats']['upload']
		total_time = state['stats']['uptime']
	except FileNotFoundError: # empty state
		wp.try_login(config['login']['email'], config['login']['password'])
		wp.login(config['login']['computer'])

	inputs = list(config['inputs'])
	interfaces = list(config['interfaces'])

def get_bytes():
	bytes = {}
	for interface in interfaces:
		try:
			bytes[interface] = {
				'rx': int(open('/sys/class/net/' + interface + '/statistics/rx_bytes').read()),
				'tx': int(open('/sys/class/net/' + interface + '/statistics/tx_bytes').read())
			}
		except FileNotFoundError: # interface not up
			bytes[interface] = {'rx': 0, 'tx': 0}

	return bytes

def start():
	# start inputs
	global selector
	selector = selectors.DefaultSelector()
	for input in inputs:
		input = InputDevice(input)
		selector.register(input, selectors.EVENT_READ)

	# start interfaces
	global prev_bytes
	prev_bytes = get_bytes()

	global prev_time
	prev_time = time.time()

	global prev_save
	prev_save = time.time()

def pulse(signum=None, frame=None):
	stats = whatpulse.Stats(keys=keys, clicks=clicks, download=round(total_bytes['rx'] / pow(BYTE_BASE, 2)), upload=round(total_bytes['tx'] / pow(BYTE_BASE, 2)), uptime=round(total_time))

	try:
		wp.client_login()
		wp.pulse(stats)
		reset_stats()
	except requests.exceptions.ConnectionError as e:
		pass # TODO: retry pulse

def autopulse():
	for key, cond in config['pulse'].items():
		value = None
		if key == 'keys':
			value = keys
			cond = converter.general(cond)
		elif key == 'clicks':
			value = clicks
			cond = converter.general(cond)
		elif key == 'download':
			value = total_bytes['rx']
			cond = converter.size(cond)
		elif key == 'upload':
			value = total_bytes['tx']
			cond = converter.size(cond)
		elif key == 'uptime':
			value = total_time
			cond = converter.time(cond)

		if value >= cond:
			pulse()
			break

def save_state():
	state_file = open(STATE_FILE, 'w')
	state = {
		'login': {
			'userid': wp.userid,
			'computerid': wp.computerid,
			'hash': wp.hash,
			'token': wp.token
		},
		'stats': {
			'keys': keys,
			'clicks': clicks,
			'download': total_bytes['rx'],
			'upload': total_bytes['tx'],
			'uptime': total_time
		}
	}
	json.dump(state, state_file)

def autostate():
	try:
		global prev_save
		cur_save = time.time()

		if prev_save + converter.time(config['state']['interval']) <= cur_save:
			save_state()
			prev_save = cur_save
	except KeyError as e: # no interval specified
		pass

def main_loop():
	# handle inputs
	global keys, clicks
	for key, mask in selector.select(1): # TODO: more efficient timeout
		input = key.fileobj
		for ev in input.read():
			if ev.type == ecodes.EV_KEY:
				keyev = KeyEvent(ev) # turn into KeyEvent
				if keyev.keystate == KeyEvent.key_up:
					if ev.code < 255: # arbitary limit
						keys += 1
					else:
						clicks += 1

	# handle interfaces
	global prev_bytes, total_bytes
	cur_bytes = get_bytes()
	for interface, bytes in cur_bytes.items():
		diff = {
			'rx': bytes['rx'] - prev_bytes[interface]['rx'],
			'tx': bytes['tx'] - prev_bytes[interface]['tx']
		}

		# handle stat counter reset
		if diff['rx'] < 0:
			diff['rx'] += pow(2, 32) # is rollever always at 2^32?
		if diff['tx'] < 0:
			diff['tx'] += pow(2, 32)

		total_bytes['rx'] += diff['rx']
		total_bytes['tx'] += diff['tx']

	prev_bytes = cur_bytes

	# handle time
	global prev_time, total_time
	cur_time = time.time()
	total_time += cur_time - prev_time
	prev_time = cur_time

	autopulse()
	autostate()

def cleanup(signum, frame):
	save_state()
	sys.exit(0)

context = daemon.DaemonContext(
	working_directory='.',
	pidfile=lockfile.FileLock(LOCK_FILE),
	stdout=stdout_file,
	stderr=stderr_file
)

context.signal_map = {
	signal.SIGTERM: cleanup,
	signal.SIGHUP: 'terminate',
	signal.SIGUSR1: pulse
}

setup()
with context:
	start()
	while True:
		main_loop()

