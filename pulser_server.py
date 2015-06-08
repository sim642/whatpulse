import whatpulse, time

wp = whatpulse.Client()
wp.try_login('whattester@mailinator.com', 'whattester')
wp.login('py_s')
wp.client_login()

interfaces = ['wlan0']

def bytes(interfaces):
	ret = {}
	for interface in interfaces:
		ret[interface] = {
			'rx': int(open('/sys/class/net/' + interface + '/statistics/rx_bytes').read()),
			'tx': int(open('/sys/class/net/' + interface + '/statistics/tx_bytes').read())
		}
	return ret

prev_bytes = bytes(interfaces)
prev_time = time.time()

while True:
	# handle interfaces
	cur_bytes = bytes(interfaces)
	total_bytes = {'rx': 0, 'tx': 0}
	for interface in interfaces:
		diff = {
			'rx': cur_bytes[interface]['rx'] - prev_bytes[interface]['rx'],
			'tx': cur_bytes[interface]['tx'] - prev_bytes[interface]['tx']
		}

		# handle stat counter reset
		if diff['rx'] < 0:
			diff['rx'] += pow(2, 32)
		if diff['tx'] < 0:
			diff['tx'] += pow(2, 32)

		total_bytes['rx'] += diff['rx']
		total_bytes['tx'] += diff['tx']

	cur_time = time.time()
	diff_time = int(cur_time - prev_time)

	prev_bytes = cur_bytes
	prev_time = cur_time

	stats = whatpulse.Stats(download=total_bytes['rx'] // (1024 * 1024), upload=total_bytes['tx'] // (1024 * 1024), uptime=diff_time)
	print(stats)
	res = wp.pulse(stats)
	print(res.status)

	time.sleep(60)
