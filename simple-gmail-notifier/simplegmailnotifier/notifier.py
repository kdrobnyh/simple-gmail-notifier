#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Based on the Gmail Notifier project: http://sourceforge.net/projects/gmail-notify/
# Maintainer: Klim Drobnyh <klim.drobnyh@gmail.com>

import pygtk
pygtk.require('2.0')
import gtk
import logging
import os
import subprocess
import time

from .config import ConfigWindow
from .connect import Receiver
from .popup import PopupMenu
from .constants import Constants


class Notifier(object):
    config = None
    started = False

    def __init__(self, path):
        self.icon_path_small = path + "resources/icons/small.png"
        self.icon_path_empty = path + "resources/icons/empty.png"
        self.icon_path_notempty = path + "resources/icons/notempty.png"
        self.icon_path_new = path + "resources/icons/new.png"
        self.icon_path_warning = path + "resources/icons/warning.png"
        self.sound_path_incoming = path + "resources/sounds/incoming.wav"
        self.constants = Constants()
        self.critical_errors = [self.constants.get_auterror(), self.constants.get_nologin()]
        self.status = self.constants.get_nologin()
        logging.info("Simple Gmail Notifier (" + time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()) + ")")
        self.config = ConfigWindow(path)
        self.options = self.config.options
        self.lang = self.config.get_lang()
        logging.info("Selected language: " + self.config.get_lang_name())
        self.mails = []
        self.mailcheck = False
        self.maintimer = None
        self.tray = gtk.StatusIcon()
        self.tray.set_title(self.lang["program"])
        self.tray.connect("button_press_event", self.tray_icon_clicked)
        self.icon_small = gtk.gdk.pixbuf_new_from_file(self.icon_path_small)
        self.icon_empty = gtk.gdk.pixbuf_new_from_file(self.icon_path_empty)
        self.icon_notempty = gtk.gdk.pixbuf_new_from_file(self.icon_path_notempty)
        self.icon_warning = gtk.gdk.pixbuf_new_from_file(self.icon_path_warning)
        gtk.window_set_default_icon_list(self.icon_small)
        self.icon_size = self.tray.get_size()
        scaled_buf = self.scale_icon_to_system_tray(self.icon_empty)
        self.tray.set_from_pixbuf(scaled_buf)
        while gtk.events_pending():
            gtk.main_iteration(gtk.TRUE)
        self.connection = Receiver(self.options['gmailusername'], self.options['gmailpassword'])
        self.status = self.constants.get_ok()
        self.start_update()

    def scale_icon_to_system_tray(self, icon):
        return icon.scale_simple(self.icon_size, self.icon_size, gtk.gdk.INTERP_BILINEAR)

    def warning_message(self, text):
        try:
            subprocess.call(['notify-send', self.lang["program"], text, "-i", self.icon_path_warning, "-t", str(self.options["popuptimespan"])])
        except:
            logging.info("Notifier error")

    def show_new_messages(self, mails, new=True):
        l = len(mails)
        if l > 0:
            text = "<b>%s</b>\n" % (self.lang["messages_new"] % l if new else self.lang["messages_unread"] % l)
            for mail in mails:
                text += "\n<b>" + self.lang["message"] % ("</b>%s<%s><b>" % (mail.author_name, mail.author_addr), "</b>%s<b>" % mail.title, "</b>" + mail.summary) + "\n"
            try:
                subprocess.call(['notify-send', self.lang["program"], text, "-i", self.icon_path_new, "-t", str(self.options["popuptimespan"])])
            except:
                logging.info("Notifier error")
            if new:
                try:
                    subprocess.call(['aplay', self.sound_path_incoming])
                except:
                    logging.info("Play sound error")

    def start_update(self, event=None):
        logging.debug("Starting update")
        if not self.started:
            self.mail_check()
            if self.status == self.constants.get_ok():
                self.maintimer = gtk.timeout_add(self.options['checkinterval'], self.mail_check)
                self.started = True
                self.popup_menu = PopupMenu(self)

    def stop_update(self, event=None):
        logging.debug("Stopping update")
        if self.started:
            gtk.timeout_remove(self.maintimer)
            self.started = False
            self.popup_menu = PopupMenu(self)

    def mail_check(self, event=None, unread=False):
        if self.mailcheck:
            logging.info("Mailcheck is already run")
            return gtk.TRUE
        self.mailcheck = True
        logging.info("Checking for new mail (" + time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()) + ")")
        while gtk.events_pending():
            gtk.main_iteration(gtk.TRUE)
        result = self.refresh()
        status = result[0]
        if status == self.constants.get_ok():
            messages = result[1]
            messages_count = len(messages)
            if messages_count > 0:
                logging.info("You have %i unread messages" % messages_count)
                to_show = [mail for mail in messages if mail not in self.mails]
                if to_show:
                    logging.info("You receive %i new messages!" % len(to_show))
                self.show_new_messages(to_show)
                if not (messages_count == len(self.mails) and self.status == self.constants.get_ok()):
                    self.tray.set_tooltip_text(self.lang["messages_unread"] % messages_count)
                    pixmap = self.scale_icon_to_system_tray(self.icon_notempty).render_pixmap_and_mask(alpha_threshold=127)[0]
                    label = gtk.Label(str(messages_count))
                    textLay = label.create_pango_layout("")
                    textLay.set_markup('<span font_desc="Sans bold %i" foreground="#010101">%s</span>' % (self.icon_size / 3, str(messages_count)))
                    (text_w, text_h) = textLay.get_pixel_size()
                    x = 2 * (self.icon_size - text_w) / 3
                    y = self.icon_size / 4 + int((0.85 * self.icon_size - text_h) / 2)
                    pixmap.draw_layout(pixmap.new_gc(), x, y, textLay)
                    trayPixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, self.icon_size, self.icon_size)
                    trayPixbuf.get_from_drawable(pixmap, pixmap.get_colormap(), 0, 0, 0, 0, self.icon_size, self.icon_size)
                    pixbuf = trayPixbuf.add_alpha(True, 0, 0, 0)
                    self.tray.set_from_pixbuf(self.scale_icon_to_system_tray(pixbuf))
                    logging.debug("Updating picture")
                if unread:
                    self.show_new_messages(messages, new=False)
            else:
                logging.info("No new messages")
                if not (len(self.mails) == 0 and self.status == self.constants.get_ok()):
                    self.tray.set_tooltip_text(self.lang["messages_empty"])
                    self.tray.set_from_pixbuf(self.scale_icon_to_system_tray(self.icon_empty))
                    logging.debug("Updating picture")
            self.status = status
            self.popup_menu = PopupMenu(self)
            self.mails = messages
            self.mailcheck = False
            return gtk.TRUE
        else:
            if not status == self.status or unread:
                message = self.lang["connect_nologin"] if status == self.constants.get_nologin() else \
                          self.lang["connect_autherror"] if status == self.constants.get_auterror() else \
                          self.lang["connect_parseerror"] if status == self.constants.get_parseerror() else \
                          self.lang["connect_connerror"]
                self.tray.set_tooltip_text(message)
                self.warning_message(message)
            if self.status == self.constants.get_ok():
                self.mails = []
                self.tray.set_from_pixbuf(self.scale_icon_to_system_tray(self.icon_warning))
                logging.debug("Updating picture")
            if self.started and status in self.critical_errors:
                self.stop_update()
            self.status = status
            self.popup_menu = PopupMenu(self)
            self.mailcheck = False
            return gtk.FALSE if status in self.critical_errors else gtk.TRUE

    def refresh(self):
        status = self.connection.refresh()
        if status == self.constants.get_nologin():
            logging.info("No login/password")
            return (status, )
        if status == self.constants.get_auterror():
            logging.info("Wrong login/password")
            return (status, )
        if status == self.constants.get_connectionerror():
            logging.info("Connection error")
            return (status, )
        if status == self.constants.get_parseerror():
            logging.info("Parsing error")
            return (status, )
        if status == self.constants.get_ok():
            return (status, self.connection.get_mails())

    def tray_icon_clicked(self, signal, event):
        if event.button == 3:
            self.popup_menu.show_menu(event)
        else:
            self.mail_check(unread=True)

    def exit(self, event):
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, self.lang["exit"])
        dialog.set_position(gtk.WIN_POS_CENTER)
        dialog.set_title(self.lang["program"])
        ret = dialog.run()
        if(ret == gtk.RESPONSE_YES):
            gtk.main_quit(0)
        dialog.destroy()

    def gotourl(self, event):
        logging.info("launching browser " + self.options['browserpath'] + " http://gmail.google.com")
        os.system(self.options['browserpath'] + " http://gmail.google.com &")

    def update_config(self, event=None):
        logging.debug("Updating config")
        if self.started:
            gtk.timeout_remove(self.maintimer)
        self.config.show()
        self.lang = self.config.get_lang()
        self.connection = Receiver(self.options["gmailusername"], self.options["gmailpassword"])
        if self.started:
            self.start_update()
        else:
            self.mail_check()
        self.popup_menu = PopupMenu(self)

    def main(self):
        gtk.main()
