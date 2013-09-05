#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Based on the Gmail Notifier project: http://sourceforge.net/projects/gmail-notify/
# Maintainer: Klim Drobnyh <klim.drobnyh@gmail.com>

import logging
import sys
sys.path[0] = "/home/kad/projects/git/gmail-notifier/simple-gmail-notifier/"
from simplegmailnotifier.notifier import Notifier

logging.basicConfig(format="%(module)s:%(funcName)s()  %(message)s", level=logging.DEBUG)
notifier = Notifier(sys.path[0])
notifier.main()
