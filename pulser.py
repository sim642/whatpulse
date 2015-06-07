from evdev import categorize, ecodes
from ev2 import ReadInputDevice
import selectors

inputs = ['/dev/input/event3', '/dev/input/event2']
interfaces = ['wlan0', 'lo']

def bytes(interfaces):
	ret = {}
	for interface in interfaces:
		ret[interface] = {
			'rx': int(open('/sys/class/net/' + interface + '/statistics/rx_bytes').read()),
			'tx': int(open('/sys/class/net/' + interface + '/statistics/tx_bytes').read())
		}
	return ret

selector = selectors.DefaultSelector()
for input in inputs:
	input = ReadInputDevice(input)
	print(input.capabilities(verbose=True))
	selector.register(input, selectors.EVENT_READ)

keys = 0
clicks = 0
prev_bytes = bytes(interfaces)
total_bytes = {'rx': 0, 'tx': 0}

while True:
	# handle inputs
	for key, mask in selector.select(1):
		input = key.fileobj
		for ev in input.read():
			if ev.type == ecodes.EV_KEY:
				keyev = categorize(ev) # turn into KeyEvent
				if keyev.keystate == keyev.key_up:
					if ev.code < 255: # kind of random limit
						keys += 1
					else:
						clicks += 1

	# handle interfaces
	cur_bytes = bytes(interfaces)
	diff_bytes = {}
	for interface in interfaces:
		diff_bytes[interface] = {
			'rx': cur_bytes[interface]['rx'] - prev_bytes[interface]['rx'],
			'tx': cur_bytes[interface]['tx'] - prev_bytes[interface]['tx']
		}

		total_bytes['rx'] += diff_bytes[interface]['rx']
		total_bytes['tx'] += diff_bytes[interface]['tx']

	prev_bytes = cur_bytes

	print((keys, clicks, total_bytes['rx'] // (1024 * 1024), total_bytes['tx'] // (1024 * 1024)), total_bytes)
