#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# This project based on Gmail Notifier project: http://sourceforge.net/projects/gmail-notify/
# Maintainer: Klim Drobnyh <klim.drobnyh@gmail.com>

from xml import sax
import collections
import logging


# Language XML file parser
class LangHandler(sax.handler.ContentHandler):

    def __init__(self):
        self.langs = collections.defaultdict(lambda: collections.defaultdict(lambda: "(empty)"))
        self.temp_lang = collections.defaultdict(lambda: "(empty)")
        self.temp_s = ""

    def startElement(self, name, attrs):
        if name == "lang":
            self.temp_lang = collections.defaultdict(lambda: "(empty)")
            self.langs[attrs.getValue("name")] = self.temp_lang
        if name == "string":
            self.temp_s = attrs.getValue("id")

    def endElement(self, name):
        pass

    def characters(self, content):
        if not content.strip() == "":
            self.temp_lang[self.temp_s] = content


# The main class
class NotifierLangsParser(object):
    def __init__(self, filename):
        self.lh = LangHandler()
        try:
            sax.parse(filename, self.lh)
            logging.info("notifierlangsparser: XML file succesfully parsed")
        except:
            logging.info("notifierlangsparser: Error parsing XML file.")

    def get_lang(self, langname):
        return self.lh.langs[langname]

    def get_langs(self):
        return self.lh.langs.keys()