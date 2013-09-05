#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Based on the Gmail Notifier project: http://sourceforge.net/projects/gmail-notify/
# Maintainer: Klim Drobnyh <klim.drobnyh@gmail.com>


class Constants(object):

    def get_ok(self):
        return 0

    def get_connectionerror(self):
        return 1

    def get_auterror(self):
        return 2

    def get_nologin(self):
        return 3

    def get_parseerror(self):
        return 4
