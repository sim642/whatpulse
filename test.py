import whatpulse as wp

s = wp.Session()
pt = wp.ProxyTestRequest()

ret = s.request(pt)
print(ret)
