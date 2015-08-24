import sys, re

search = open('search.pem', 'rb').read()
replace = open('replace.pem', 'rb').read()

def nlfix(buf, newnl):
	return re.sub(b'\r?\n', newnl, buf)

newnl = None
if sys.argv[1] == "lf":
	newnl = b'\n'
elif sys.argv[1] == "crlf":
	newnl = b'\r\n'

if newnl:
	search = nlfix(search, newnl)
	replace = nlfix(replace, newnl)

replace = replace.ljust(len(search), b'\x00')

f = open('whatpulse', 'rb').read()
f = f.replace(search, replace)
open('whatpulse-mitm', 'wb').write(f)
