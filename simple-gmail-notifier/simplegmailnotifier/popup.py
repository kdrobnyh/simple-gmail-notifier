#!/usr/bin/python2
# -*- coding: utf-8 -*-

# Based on the Gmail Notifier project: http://sourceforge.net/projects/gmail-notify/
# Maintainer: Klim Drobnyh <klim.drobnyh@gmail.com>

import gtk
from .constants import Constants


class PopupMenu(object):
    def __init__(self, gmailnotifier):
        self.constants = Constants()

        self.item_check = gtk.MenuItem(gmailnotifier.lang["menu_check"], gtk.TRUE)
        self.item_inbox = gtk.MenuItem(gmailnotifier.lang["menu_inbox"], gtk.TRUE)
        self.item_start = gtk.MenuItem(gmailnotifier.lang["menu_refreshing_start"], gtk.TRUE)
        self.item_stop = gtk.MenuItem(gmailnotifier.lang["menu_refreshing_stop"], gtk.TRUE)
        self.item_conf = gtk.MenuItem(gmailnotifier.lang["menu_configure"], gtk.TRUE)
        self.item_exit = gtk.MenuItem(gmailnotifier.lang["menu_exit"], gtk.TRUE)

        self.item_check.connect('activate', gmailnotifier.mail_check)
        self.item_inbox.connect('activate', gmailnotifier.gotourl)
        self.item_start.connect('activate', gmailnotifier.start_update)
        self.item_stop.connect('activate', gmailnotifier.stop_update)
        self.item_conf.connect('activate', gmailnotifier.update_config)
        self.item_exit.connect('activate', gmailnotifier.exit)

        self.menu = gtk.Menu()
        if not gmailnotifier.status == self.constants.get_nologin():
            self.menu.append(self.item_check)
            self.menu.append(self.item_inbox)
            self.menu.append(gtk.SeparatorMenuItem())
            if (gmailnotifier.started):
                self.menu.append(self.item_stop)
            else:
                self.menu.append(self.item_start)
            self.menu.append(gtk.SeparatorMenuItem())
        self.menu.append(self.item_conf)
        self.menu.append(gtk.SeparatorMenuItem())
        self.menu.append(self.item_exit)
        self.menu.show_all()

    def show_menu(self, event):
        self.menu.popup(None, None, None, event.button, event.time)