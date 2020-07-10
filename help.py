#!/usr/bin/env python


import sys
sys.path.insert(0, '/home/amitroi')
exec('from {} import script_description'.format(sys.argv[1]))


print(script_description())
