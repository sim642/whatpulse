from lxml import etree

class Stats(object):
	def __init__(self, keys=0, clicks=0, download=0, upload=0, uptime=0):
		self.keys = keys
		self.clicks = clicks
		self.download = download
		self.upload = upload
		self.uptime = uptime

	def __repr__(self):
		return repr({
			'keys': self.keys,
			'clicks': self.clicks,
			'download': self.download,
			'upload': self.upload,
			'uptime': self.uptime
		})

	@staticmethod
	def parse(tree, name):
		ret = Stats()
		for elem in tree:
			if elem.tag.startswith(name):
				key = elem.tag[len(name):]
				value = int(elem.text)
				setattr(ret, key, value)
		return ret

	dump_map = {
		'keys': 'keycount',
		'clicks': 'clickcount',
		'download': 'download',
		'upload': 'upload',
		'uptime': 'uptime'
	}

	def dump(self):
		elems = []
		for key, to in self.dump_map.items():
			elem = etree.Element(to)
			elem.text = str(getattr(self, key))
			elems.append(elem)
		return elems
