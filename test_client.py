import whatpulse

wp = whatpulse.Client()
wp.try_login('whattester@mailinator.com', 'whattester')
wp.login('py')
wp.client_login()

#wp.pulse(whatpulse.Stats(clicks=10, download=5, upload=1, uptime=100))
