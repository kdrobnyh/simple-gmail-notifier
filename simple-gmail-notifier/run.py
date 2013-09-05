#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Based on the Gmail Notifier project: http://sourceforge.net/projects/gmail-notify/
# Maintainer: Klim Drobnyh <klim.drobnyh@gmail.com>

import logging
import os
import sys
sys.path[0] = "/home/kad/projects/git/simple-gmail-notifier/simple-gmail-notifier/"
from simplegmailnotifier.notifier import Notifier

logfile = os.path.expanduser("~/.config/simple-gmail-notifier/logs")
try:
    d = os.path.dirname(logfile)
    if not os.path.exists(d):
        os.makedirs(d)
    f = open(logfile, 'w')
    f.close()
except:
    logging.critical("Can't access logfile: %s" % logfile)
    exit(1)
logging.basicConfig(format="%(levelname)s: %(module)s:%(funcName)s()  %(message)s", level=logging.DEBUG, filename=logfile)
notifier = Notifier(sys.path[0])
notifier.main()
