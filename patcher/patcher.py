# TODO: choice to handle \r\n line endings instead for .exe
search = open('search.pem', 'rb').read()
replace = open('replace.pem', 'rb').read()

replace = replace.ljust(len(search), b'\x00')

f = open('whatpulse', 'rb').read()
f = f.replace(search, replace)
open('whatpulse-mitm', 'wb').write(f)
