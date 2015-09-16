import whatpulse as wp

s = wp.Session()
#pt = wp.ProxyTestRequest()
tl = wp.TryLoginRequest('whattester@mailinator.com', 'whattester')
ret1 = s.request(tl)

l = wp.LoginRequest('whattester@mailinator.com', ret1.hash, 'py')
ret2 = s.request(l)

cl = wp.ClientLoginRequest(ret2.userid, ret2.computerid, ret1.hash)
ret3 = s.request(cl)

p = wp.PulseRequest(ret3.client_token, ret2.token, wp.Stats(keys=100))
ret4 = s.request(p)
