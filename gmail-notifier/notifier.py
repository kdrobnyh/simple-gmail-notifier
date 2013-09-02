#!/usr/bin/python2
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
import time
import os
import sys
import notifierconfig
import notifieratom
import notifierpopup
import notifierconstants
import logging
import subprocess

#sys.path[0] = "/usr/share/gmail-notify"
sys.path[0] = "/home/kad/projects/git/gmail-notifier/gmail-notifier/"
ICON_PATH_EMPTY = sys.path[0] + "gmail-notifier-empty.png"
ICON_PATH_UNREAD = sys.path[0] + "gmail-notifier-unread.png"
ICON_PATH_NEW = sys.path[0] + "gmail-notifier-new.png"
ICON_PATH_WARNING = sys.path[0] + "gmail-notifier-warning.png"
SOUND_PATH_INCOMING = sys.path[0] + "incoming.wav"


class GmailNotify:
    configWindow = None
    consts = None
    started = True

    def __init__(self):
        self.consts = notifierconstants.NotifierConstants()
        self.status = self.consts.get_nologin()
        logging.info("Gmail Notifier (" + time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()) + ")")
        # Configuration window
        self.configWindow = notifierconfig.GmailConfigWindow()
        # Reference to global options
        self.options = self.configWindow.options
        # Load selected language
        self.lang = self.configWindow.get_lang()
        logging.info("selected language: " + self.configWindow.get_lang_name())
        self.mails = []
        self.mailcheck = False
        # Define the timers
        self.maintimer = None
        # Create the tray icon object
        self.tray = gtk.StatusIcon()
        self.tray.set_title(self.lang["program_name"])
        self.tray.connect("button_press_event", self.tray_icon_clicked)
        # Set the image for the tray icon
        self.icon_empty = gtk.gdk.pixbuf_new_from_file(ICON_PATH_EMPTY)
        self.icon_unread = gtk.gdk.pixbuf_new_from_file(ICON_PATH_UNREAD)
        self.icon_size = self.tray.get_size()
        scaled_buf = self.scale_icon_to_system_tray(self.icon_empty)
        self.tray.set_from_pixbuf(scaled_buf)
        while gtk.events_pending():
            gtk.main_iteration(gtk.TRUE)
        # Attemp connection for first time
        self.connect()
        self.popup_menu = notifierpopup.GmailPopupMenu(self)

    def scale_icon_to_system_tray(self, icon):
        return icon.scale_simple(self.icon_size, self.icon_size, gtk.gdk.INTERP_BILINEAR)

    def warning_message(self, text):
        subprocess.call(['notify-send', self.lang["program_name"], text, "-i", ICON_PATH_WARNING, "-t", str(self.options["popuptimespan"])])

    def show_new_messages(self, mails, new=True):
        l = len(mails)
        if l > 0:
            if new:
                text = self.lang["new_message"] % l
            else:
                text = self.lang["unread_message"] % l
            if l > 1:
                text += "s\n"
            for mail in mails:
                text += "\n<b>" + self.lang["mail"] % ("</b>%s<%s><b>" % (mail.author_name, mail.author_addr), "</b>%s<b>" % mail.title, "</b>" + mail.summary) + "\n"
            subprocess.call(['notify-send', self.lang["program_name"], text, "-i", ICON_PATH_NEW, "-t", str(self.options["popuptimespan"])])
            if new:
                subprocess.call(['aplay', SOUND_PATH_INCOMING])

    def start_update(self, event=None):
        self.popup_menu = notifierpopup.GmailPopupMenu(self)
        self.mail_check()
        if self.status == self.consts.get_ok():
            self.maintimer = gtk.timeout_add(self.options['checkinterval'], self.mail_check)
            self.started = True
        else:
            self.started = False
            self.popup_menu = notifierpopup.GmailPopupMenu(self)

    def stop_update(self, event=None):
        if self.started:
            gtk.timeout_remove(self.maintimer)
            self.started = False
            self.popup_menu = notifierpopup.GmailPopupMenu(self)

    def connect(self):
        logging.info("Trying to connect...")
        self.tray.set_tooltip(self.lang["connecting"])
        while gtk.events_pending():
            gtk.main_iteration(gtk.TRUE)
        self.connection = notifieratom.GmailAtom(self.options['gmailusername'], self.options['gmailpassword'])
        self.status = self.connection.refreshInfo()
        if self.status == self.consts.get_nologin():
            logging.info("No login/password")
            self.tray.set_tooltip_text(self.lang["nologin"])
            self.warning_message(self.lang["nologin"])
            self.started = False
        if self.status == self.consts.get_auterror():
            logging.info("Wrong login/password")
            self.tray.set_tooltip_text(self.lang["autherror"])
            self.warning_message(self.lang["autherror"])
            self.started = False
        if self.status == self.consts.get_connectionerror():
            logging.info("Connection error")
            self.tray.set_tooltip_text(self.lang["connerror"])
            self.warning_message(self.lang["connerror"])
            self.started = True
        if self.status == self.consts.get_parseerror():
            logging.info("Parsing error")
            self.tray.set_tooltip_text(self.lang["parseerror"])
            self.warning_message(self.lang["parseerror"])
            self.started = True
        if self.status == self.consts.get_ok():
            logging.info("Connection successful! Continuing...")
            self.started = True
            self.tray.set_tooltip_text(self.lang["connected"])
            self.maintimer = gtk.timeout_add(self.options['checkinterval'], self.mail_check)
            self.mail_check()

    def mail_check(self, event=None, unread=False):
        # If checking, cancel mail check
        if self.mailcheck:
            logging.info("Mailcheck is already run")
            return gtk.TRUE
        self.mailcheck = True
        logging.info("Checking for new mail (" + time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()) + ")")
        while gtk.events_pending():
            gtk.main_iteration(gtk.TRUE)

        # Get new messages count
        messages = self.get_unread_messages()

        # If mail check was unsuccessful
        if messages is None:
            logging.info("Unsuccessful mail check")
            self.mailcheck = False
            return gtk.TRUE

        messages_count = len(messages)
        if messages_count > 0:
            to_show = []
            logging.info("You have %i unread messages" % messages_count)
            for mail in messages:
                if mail not in self.mails:
                    logging.info("New message!")
                    to_show.append(mail)
            self.show_new_messages(to_show)
            text = self.lang["unread_message"] % messages_count
            if messages_count > 0:
                text += "s"
            self.tray.set_tooltip_text(text)
            pixmap = self.scale_icon_to_system_tray(self.icon_unread).render_pixmap_and_mask(alpha_threshold=127)[0]
            label = gtk.Label(str(messages_count))
            textLay = label.create_pango_layout("")
            textLay.set_markup('<span font_desc="Sans bold %i" foreground="#010101">%s</span>' % (self.icon_size / 3, str(messages_count)))
            (text_w, text_h) = textLay.get_pixel_size()
            x = 2 * (self.icon_size - text_w) / 3
            y = self.icon_size / 4 + int((0.85 * self.icon_size - text_h) / 2)

            ## Finally draw the text and apply in status icon
            pixmap.draw_layout(pixmap.new_gc(), x, y, textLay)  # foreground, background)
            trayPixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, self.icon_size, self.icon_size)
            trayPixbuf.get_from_drawable(pixmap, pixmap.get_colormap(), 0, 0, 0, 0, self.icon_size, self.icon_size)
            pixbuf = trayPixbuf.add_alpha(True, 0, 0, 0)
            #cmap = gtk.gdk.Colormap(gtk.gdk.visual_get_system(), False)

            self.mails = messages
            if unread:
                self.show_new_messages(messages, new=False)
        else:
            logging.info("No new messages")
            self.tray.set_tooltip_text(self.lang["no unread"])
            pixbuf = self.icon_empty
        scaled_buf = self.scale_icon_to_system_tray(pixbuf)
        self.tray.set_from_pixbuf(scaled_buf)
        self.mailcheck = False
        return gtk.TRUE

    def get_unread_messages(self):
        # Get total messages in inbox
        self.status = self.connection.refreshInfo()
        if self.status == self.consts.get_nologin():
            logging.info("No login/password")
            self.tray.set_tooltip_text(self.lang["nologin"])
            self.warning_message(self.lang["nologin"])
            self.started = False
            return None
        if self.status == self.consts.get_auterror():
            logging.info("Wrong login/password")
            self.tray.set_tooltip_text(self.lang["autherror"])
            self.warning_message(self.lang["autherror"])
            self.started = False
            return None
        if self.status == self.consts.get_connectionerror():
            logging.info("Connection error")
            self.tray.set_tooltip_text(self.lang["connerror"])
            self.warning_message(self.lang["connerror"])
            return None
        if self.status == self.consts.get_parseerror():
            logging.info("Parsing error")
            self.tray.set_tooltip_text(self.lang["parseerror"])
            self.warning_message(self.lang["parseerror"])
            return None
        if self.status == self.consts.get_ok():
            return self.connection.get_mails()

    def tray_icon_clicked(self, signal, event):
        if event.button == 3:
            self.popup_menu.show_menu(event)
        else:
            self.mail_check(unread=True)

    def event_box_clicked(self, signal, event):
        if event.button == 1:
            self.gotourl()

    def exit(self, event):
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, self.lang["on_exit"])
        dialog.width, dialog.height = dialog.get_size()
        dialog.move(gtk.gdk.screen_width() / 2 - dialog.width / 2, gtk.gdk.screen_height() / 2 - dialog.height / 2)
        ret = dialog.run()
        if(ret == gtk.RESPONSE_YES):
            gtk.main_quit(0)
        dialog.destroy()

    def gotourl(self):
        logging.info("launching browser " + self.options['browserpath'] + " http://gmail.google.com")
        os.system(self.options['browserpath'] + " http://gmail.google.com &")

    def update_config(self, event=None):
        # Kill all timers
        if self.started:
            gtk.timeout_remove(self.maintimer)
        # Run the configuration dialog
        self.configWindow.show()
        # Update user/pass
        self.connection = notifieratom.GmailAtom(self.options["gmailusername"], self.options["gmailpassword"])
        self.connect()
        self.popup_menu = notifierpopup.GmailPopupMenu(self)
        # Update language
        self.lang = self.configWindow.get_lang()
        # Update popup menu
        self.popup_menu = notifierpopup.GmailPopupMenu(self)
        return

    def main(self):
        gtk.main()

if __name__ == "__main__":
    logging.basicConfig(format="%(module)s:%(funcName)s()  %(message)s", level=logging.DEBUG)
    gmailnotifier = GmailNotify()
    gmailnotifier.main()
