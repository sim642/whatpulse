import whatpulse as wp

s = wp.Session()
#pt = wp.ProxyTestRequest()
tl = wp.TryLoginRequest('whattester@mailinator.com', 'whattester')
ret = s.request(tl)

l = wp.LoginRequest('whattester@mailinator.com', ret.hash, 'py')
ret = s.request(l)

