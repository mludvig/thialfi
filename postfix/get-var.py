#!/usr/bin/env python

import sys
try:
    exec(compile(open(sys.argv[1]).read(), sys.argv[1], 'exec'))
    print(locals()[sys.argv[2]])
except:
    pass
