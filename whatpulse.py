import requests
from lxml import etree

class WhatPulse(object):
	client_version = '2.6.1'

	def query(self, xml):
		payload = {'client_version': self.client_version, 'xml': xml}
		headers = {'User-Agent': 'WhatPulse Client ' + self.client_version}
		r = requests.post('https://client.whatpulse.org/v1.1/', verify='whatpulse.pem', headers=headers, data=payload)

		return etree.fromstring(r.text)

	def test(self):
		xml = '<?xml version="1.0" encoding="UTF-8"?><client><requests><request type="testproxy"><type_os>linux</type_os><client_version>' + self.client_version + '</client_version></request></requests></client>'

		print(etree.tostring(self.query(xml), pretty_print=True))

