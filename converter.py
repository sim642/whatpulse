import re

piece_re = re.compile('(\d+)(\w|$)', re.I)

def make_converter(mags):
	mags.append(('', 1))
	def converter(str):
		cnts = [0] * (len(mags))
		for cnt, c in re.findall(piece_re, str):
			for i, mag in enumerate(mags):
				if mag[0] == c:
					cnts[i] += int(cnt)

		val = 0
		for mag, cnt in zip(mags, cnts):
			val += cnt
			val *= mag[1]
		return val

	return converter

general = make_converter([
	('t', 1000), # tera
	('g', 1000), # giga
	('m', 1000), # mega
	('k', 1000)  # kilo
])

size = make_converter([
	('t', 1024), # tera
	('g', 1024), # giga
	('m', 1024), # mega
	('k', 1024)  # kilo
])

time = make_converter([
	('y', 52), # year
	('w', 7),  # week
	('d', 24), # day
	('h', 60), # hour
	('m', 60), # minute
	('s', 1)   # second
])
