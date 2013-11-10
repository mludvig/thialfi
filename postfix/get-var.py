#!/usr/bin/env python

import sys
try:
    execfile(sys.argv[1])
    print locals()[sys.argv[2]]
except:
    pass
