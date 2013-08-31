#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import gtk
import constants

class GmailPopupMenu:
    def __init__(self, gmailnotify):
        self.const = constants.Constants()
        # Create menu items
        self.item_check = gtk.MenuItem( gmailnotify.lang.get_string(9), gtk.TRUE)
        self.item_inbox = gtk.MenuItem( gmailnotify.lang.get_string(23), gtk.TRUE)
        self.item_start = gtk.MenuItem(gmailnotify.lang.get_string(36),  gtk.TRUE)
        self.item_stop = gtk.MenuItem(gmailnotify.lang.get_string(37),  gtk.TRUE)
        self.item_conf  = gtk.MenuItem( gmailnotify.lang.get_string(11), gtk.TRUE)
        self.item_exit = gtk.MenuItem( gmailnotify.lang.get_string(12), gtk.TRUE)
        
        # Connect the events
        self.item_check.connect( 'activate', gmailnotify.mail_check)
        self.item_inbox.connect( 'activate', gmailnotify.gotourl)
        self.item_start.connect('activate',  gmailnotify.start_update)
        self.item_stop.connect('activate',  gmailnotify.stop_update)
        self.item_conf.connect( 'activate', gmailnotify.update_config)
        self.item_exit.connect( 'activate', gmailnotify.exit)
        # Create the menu
        
        self.menu = gtk.Menu()
        if (gmailnotify.status != self.const.get_nologin()):
            self.menu.append( self.item_check)
            self.menu.append( self.item_inbox)
            self.menu.append( gtk.SeparatorMenuItem())
            if (gmailnotify.started):
                self.menu.append( self.item_stop)
            else:
                self.menu.append( self.item_start)
            self.menu.append( gtk.SeparatorMenuItem())
            
        self.menu.append( self.item_conf)
        self.menu.append( gtk.SeparatorMenuItem())
        self.menu.append( self.item_exit)
        self.menu.show_all()
        return

    def show_menu(self, event):
        # Display the menu
        self.menu.popup( None, None, None, event.button, event.time)
        return
