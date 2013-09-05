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
    TAG_FULLCOUNT = "fullcount"
    TAG_ENTRY = "entry"
    TAG_TITLE = "title"
    TAG_SUMMARY = "summary"
    TAG_AUTHOR = "author"
    TAG_NAME = "name"
    TAG_EMAIL = "email"

    PATH_FULLCOUNT = [TAG_FEED, TAG_FULLCOUNT]
    PATH_TITLE = [TAG_FEED, TAG_ENTRY, TAG_TITLE]
    PATH_SUMMARY = [TAG_FEED, TAG_ENTRY, TAG_SUMMARY]
    PATH_AUTHOR_NAME = [TAG_FEED, TAG_ENTRY, TAG_AUTHOR, TAG_NAME]
    PATH_AUTHOR_EMAIL = [TAG_FEED, TAG_ENTRY, TAG_AUTHOR, TAG_EMAIL]

    def __init__(self):
        self.startDocument()

    def startDocument(self):
        self.entries = list()
        self.actual = list()
        self.mail_count = "0"

    def startElement(self, name, attrs):
        self.actual.append(name)

        if name == "entry":
            m = Mail()
            self.entries.append(m)

    def endElement(self, name):
        self.actual.pop()

    def characters(self, content):
        if (self.actual == self.PATH_FULLCOUNT):
            self.mail_count = self.mail_count + content

        if (self.actual == self.PATH_TITLE):
            temp_mail = self.entries.pop()
            temp_mail.title = temp_mail.title + content
            self.entries.append(temp_mail)

        if (self.actual == self.PATH_SUMMARY):
            temp_mail = self.entries.pop()
            temp_mail.summary = temp_mail.summary + content
            self.entries.append(temp_mail)

        if (self.actual == self.PATH_AUTHOR_NAME):
            temp_mail = self.entries.pop()
            temp_mail.author_name = temp_mail.author_name + content
            self.entries.append(temp_mail)

        if (self.actual == self.PATH_AUTHOR_EMAIL):
            temp_mail = self.entries.pop()
            temp_mail.author_addr = temp_mail.author_addr + content
            self.entries.append(temp_mail)

    def getUnreadMsgCount(self):
        return int(self.mail_count)

    def getMail(self, index):
        if index < int(self.mail_count):
            return self.entries[index]
        else:
            return Mail()


class Receiver(object):

    realm = "New mail feed"
    host = "https://mail.google.com"
    url = host + "/mail/feed/atom"
    constants = Constants()
    status = constants.get_ok()

    def __init__(self, user, pswd):
        self.m = MailHandler()
        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(self.realm, self.host, user, pswd)
        opener = urllib2.build_opener(auth_handler)
        urllib2.install_opener(opener)
        if not user or not pswd:
            self.status = self.constants.get_nologin()

    def sendRequest(self):
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

    def refreshInfo(self):
        if self.status is not self.constants.get_nologin():
            s = self.sendRequest()
            if s is not None:
                try:
                    sax.parseString(s, self.m)
                except:
                    logging.info("Parsing failed!")
                    return self.constants.get_parseerror()
        return self.status

    def getUnreadMsgCount(self):
        return self.m.getUnreadMsgCount()

    def getMsgTitle(self, index):
        return self.m.getMail(index).title

    def getMsgSummary(self, index):
        return self.m.getMail(index).summary

    def getMsgAuthorName(self, index):
        return self.m.getMail(index).author_name

    def getMsgAuthorEmail(self, index):
        return self.m.getMail(index).author_email

    def get_mails(self):
        return self.m.entries
