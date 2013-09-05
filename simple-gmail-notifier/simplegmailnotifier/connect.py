#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Based on the Gmail Notifier project: http://sourceforge.net/projects/gmail-notify/
# Maintainer: Klim Drobnyh <klim.drobnyh@gmail.com>

from xml import sax
import logging
import urllib2
from .constants import Constants


class Mail(object):

    def __init__(self):
        self.title = ""
        self.summary = ""
        self.author_name = ""
        self.author_addr = ""

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.title == other.title and self.summary == other.summary
                   and self.author_name == other.author_name and self.author_addr == other.author_addr)
        else:
            return False


class MailHandler(sax.handler.ContentHandler):
    TAG_FEED = "feed"
    TAG_ENTRY = "entry"
    TAG_TITLE = "title"
    TAG_SUMMARY = "summary"
    TAG_AUTHOR = "author"
    TAG_NAME = "name"
    TAG_EMAIL = "email"
    PATH_TITLE = [TAG_FEED, TAG_ENTRY, TAG_TITLE]
    PATH_SUMMARY = [TAG_FEED, TAG_ENTRY, TAG_SUMMARY]
    PATH_AUTHOR_NAME = [TAG_FEED, TAG_ENTRY, TAG_AUTHOR, TAG_NAME]
    PATH_AUTHOR_EMAIL = [TAG_FEED, TAG_ENTRY, TAG_AUTHOR, TAG_EMAIL]

    def __init__(self):
        self.startDocument()

    def startDocument(self):
        self.mails = []
        self.actual_path = []

    def startElement(self, name, attrs):
        self.actual_path.append(name)

        if name == "entry":
            m = Mail()
            self.mails.append(m)

    def endElement(self, name):
        self.actual_path.pop()

    def characters(self, content):
        if (self.actual_path == self.PATH_TITLE):
            temp_mail = self.mails.pop()
            temp_mail.title = temp_mail.title + content
            self.mails.append(temp_mail)

        if (self.actual_path == self.PATH_SUMMARY):
            temp_mail = self.mails.pop()
            temp_mail.summary = temp_mail.summary + content
            self.mails.append(temp_mail)

        if (self.actual_path == self.PATH_AUTHOR_NAME):
            temp_mail = self.mails.pop()
            temp_mail.author_name = temp_mail.author_name + content
            self.mails.append(temp_mail)

        if (self.actual_path == self.PATH_AUTHOR_EMAIL):
            temp_mail = self.mails.pop()
            temp_mail.author_addr = temp_mail.author_addr + content
            self.mails.append(temp_mail)


class Receiver(object):

    realm = "New mail feed"
    host = "https://mail.google.com"
    url = host + "/mail/feed/atom"
    constants = Constants()
    status = constants.get_ok()

    def __init__(self, user, pswd):
        logging.debug("Creating receiver")
        self.m = MailHandler()
        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(self.realm, self.host, user, pswd)
        opener = urllib2.build_opener(auth_handler)
        urllib2.install_opener(opener)
        if not user or not pswd:
            self.status = self.constants.get_nologin()

    def get_mails_data(self):
        try:
            self.status = self.constants.get_ok()
            s = urllib2.urlopen(self.url, None, 200).read()
            urllib2
            return s
        except urllib2.HTTPError:
            self.status = self.constants.get_auterror()
            logging.info("Autentification failed!")
            return None
        except urllib2.URLError:
            self.status = self.constants.get_connectionerror()
            logging.info("Connection failed!")
            return None

    def refresh(self):
        logging.debug("Refreshing mails")
        if self.status is not self.constants.get_nologin():
            s = self.get_mails_data()
            if s is not None:
                try:
                    sax.parseString(s, self.m)
                except:
                    logging.info("Parsing failed!")
                    return self.constants.get_parseerror()
        return self.status

    def get_mails(self):
        return self.m.mails
