#!/usr/bin/python2
# -*- coding: utf-8 -*-

# notifierlangsparser
# Languages XML parser. Return (empty) if language or string is not exist.

# Language XML file structure
#
# <?xml version="1.0" encoding="utf-8" ?>
# <langs>
#     <lang name="myLanguage">
#         <string id="1">Here goes my first string</string>
#         <string id="2">This is my second string</string>
#         ...
#     </lang>
#     ...
# </langs>
#
# by Klim Drobnyh
# klim.drobnyh@gmail.com

from xml import sax
import collections


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
        return

    def characters(self, content):
        if content.strip() != "":
            self.temp_lang[self.temp_s] = content


# The main class
class NotifierLangsParser:
    def __init__(self, filename):
        self.lh = LangHandler()
        try:
            sax.parse(filename, self.lh)
            print "notifierlangsparser: XML file succesfully parsed"
        except:
            print "notifierlangsparser: Error parsing XML file."

    def get_lang(self, langname):
        return self.lh.langs[langname]
