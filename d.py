import daemon, signal
import configparser, whatpulse
from ev2 import ReadInputDevice
from evdev import KeyEvent, ecodes
import selectors
import time
import converter

BYTE_BASE = 1024

stdout_file = open('stdout.log', 'w+')
stderr_file = open('stderr.log', 'w+')

config = configparser.ConfigParser(allow_no_value=True)
config_file = open('d.conf', 'r')

inputs = []
interfaces = []

#selector = selectors.DefaultSelector()
selector = None
wp = whatpulse.Client()

def setup():
	global inputs, interfaces
	config.read_file(config_file)

	inputs = list(config['inputs'])
	interfaces = list(config['interfaces'])


	wp.try_login(config['login']['email'], config['login']['password'])
	wp.login(config['login']['computer'])

def get_bytes():
	bytes = {}
	for interface in interfaces:
		bytes[interface] = {
			'rx': int(open('/sys/class/net/' + interface + '/statistics/rx_bytes').read()),
			'tx': int(open('/sys/class/net/' + interface + '/statistics/tx_bytes').read())
		}
	return bytes

keys = None
clicks = None
total_bytes = None
prev_bytes = None
total_time = None
prev_time = None

def reset_stats():
	global keys, clicks, total_bytes, total_time
	keys = 0;
	clicks = 0;
	total_bytes = {'rx': 0, 'tx': 0}
	total_time = 0

def start():
	reset_stats()

	# start inputs
	global selector
	selector = selectors.DefaultSelector()
	for input in inputs:
		input = ReadInputDevice(input)
		selector.register(input, selectors.EVENT_READ)
	
	# start interfaces
	global prev_bytes
	prev_bytes = get_bytes()

	global prev_time
	prev_time = time.time()

def pulse(signum=None, frame=None):
	stats = whatpulse.Stats(keys=keys, clicks=clicks, download=round(total_bytes['rx'] / pow(BYTE_BASE, 2)), upload=round(total_bytes['tx'] / pow(BYTE_BASE, 2)), uptime=round(total_time))

	wp.client_login()
	wp.pulse(stats)
	reset_stats()

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


def main_loop():
	# handle inputs
	global keys, clicks
	for key, mask in selector.select(1):
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
			diff['rx'] += pow(2, 32)
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

def cleanup(signum, frame):
	pass

context = daemon.DaemonContext(
	working_directory='.',
	detach_process=False,
	files_preserve=[config_file],
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
	
