#!/usr/bin/python2
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
import time
import os
import sys
import warnings
import notifierconfig
import notifieratom
import notifierpopup
import notifierconstants

#sys.path[0] = "/usr/share/gmail-notify"
sys.path[0] = "/home/kad/projects/git/gmail-notifier/gmail-notify/"
BKG_PATH = sys.path[0] + "background.jpg"
ICON_PATH = sys.path[0] + "icon.png"
ICON2_PATH = sys.path[0] + "icon2.png"


def removetags(text):
    raw = text.split("<b>")
    raw2 = raw[1].split("</b>")
    final = raw2[0]
    return final


def shortenstring(text, characters):
    if text is None:
        text = ""
    mainstr = ""
    length = 0
    splitstr = text.split(" ")
    for word in splitstr:
        length = length + len(word)
        if len(word) > characters:
            if mainstr == "":
                mainstr = word[0:characters]
                break
            else:
                break
        mainstr = mainstr + word + " "
        if length > characters:
            break
    return mainstr.strip()


class GmailNotify:
    configWindow = None
    const = None
    started = True

    def __init__(self):
        self.popup = False
        self.const = notifierconstants.NotifierConstants()
        self.status = self.const.get_nologin()
        print "Gmail Notifier v2.0.0 (" + time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()) + ")"
        print "----------"
        # Configuration window
        self.configWindow = notifierconfig.GmailConfigWindow()
        # Reference to global options
        self.options = self.configWindow.options
        # Load selected language
        self.lang = self.configWindow.get_lang()
        print "selected language: " + self.lang.get_name()
        # Creates the main window
        self.window = gtk.Window(gtk.WINDOW_POPUP)
        self.window.set_title(self.lang.get_string(21))
        self.window.set_resizable(1)
        self.window.set_decorated(0)
        self.window.set_keep_above(1)
        self.window.stick()
        self.window.hide()
        # Define some flags
        self.senddown = False
        self.mailcheck = False
        self.hassettimer = 0
        self.unreadmsgcount = 0
        # Define the timers
        self.maintimer = None
        self.waittimer = 0
        # Create the popup
        self.fixed = gtk.Fixed()
        self.window.add(self.fixed)
        self.fixed.show()
        self.fixed.set_size_request(0, 0)
        # Set popup's background image
        self.image = gtk.Image()
        self.image.set_from_file(BKG_PATH)
        self.image.show()
        self.fixed.put(self.image, 0, 0)
        # Set popup's label
        self.label = gtk.Label()
        self.label.set_line_wrap(1)
        self.label.set_size_request(170, 140)
        self.default_label = "<span size='large' ><i><u>" + self.lang.get_string(21) + "</u></i></span>\n\n\n" + \
            self.lang.get_string(20)
        self.label.set_markup(self.default_label)
        # Show popup
        self.label.show()
        # Create popup's event box
        self.event_box = gtk.EventBox()
        self.event_box.set_visible_window(0)
        self.event_box.show()
        self.event_box.add(self.label)
        self.event_box.set_size_request(180, 125)
        self.event_box.set_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.event_box.connect("button_press_event", self.event_box_clicked)
        # Setup popup's event box
        self.fixed.put(self.event_box, 6, 25)
        self.event_box.realize()
        self.event_box.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND1))
        # Resize and move popup's event box
        self.window.resize(180, 1)
        self.width, self.height = self.window.get_size()
        self.height += self.options['voffset']
        self.width += self.options['hoffset']
        self.window.move(gtk.gdk.screen_width() - self.width, gtk.gdk.screen_height() - self.height)
        # Create the tray icon object
        self.tray = gtk.StatusIcon()
        self.tray.set_title(self.lang.get_string(21))
        self.tray.connect("button_press_event", self.tray_icon_clicked)
        # Set the image for the tray icon
        pixbuf = gtk.gdk.pixbuf_new_from_file(ICON_PATH)
        scaled_buf = pixbuf.scale_simple(24, 24, gtk.gdk.INTERP_BILINEAR)
        self.tray.set_from_pixbuf(scaled_buf)

        while gtk.events_pending():
            gtk.main_iteration(gtk.TRUE)
        # Attemp connection for first time
        self.connect()
        self.popup_menu = notifierpopup.GmailPopupMenu(self)
        if not self.mailcheck:
            self.show_popup()

    def start_update(self, event=None):
        self.maintimer = gtk.timeout_add(self.options['checkinterval'], self.mail_check)
        self.started = True
        self.popup_menu = notifierpopup.GmailPopupMenu(self)
        self.mail_check()

    def stop_update(self, event=None):
        if self.started:
            gtk.timeout_remove(self.maintimer)
            self.started = False
            self.popup_menu = notifierpopup.GmailPopupMenu(self)

    def connect(self):
        if (self.options["gmailusername"] is None or self.options["gmailusername"] == "" or self.options["gmailpassword"] is None or self.options["gmailpassword"] == ""):
            print "No login/password"
            self.tray.set_tooltip_text(self.lang.get_string(38))
            self.status = self.const.get_nologin()
            self.started = False
            self.default_label = "<span size='large' ><u><i>" + self.lang.get_string(21) + "</i></u></span>\n\n" + self.lang.get_string(38)
            self.label.set_markup(self.default_label)
            self.show_popup()
            return
        print "connecting..."
        self.tray.set_tooltip(self.lang.get_string(13))
        while gtk.events_pending():
            gtk.main_iteration(gtk.TRUE)
        # Attemp connection
        try:
            self.connection = notifieratom.GmailAtom(self.options['gmailusername'], self.options['gmailpassword'])
            self.connection.refreshInfo()
            print "connection successful... continuing"
            self.tray.set_tooltip_text(self.lang.get_string(14))
            self.status = self.const.get_ok()
            self.maintimer = gtk.timeout_add(self.options['checkinterval'], self.mail_check)
            self.started = True
            self.mail_check()
        except:
            print "login failed, will retry"
            self.tray.set_tooltip_text(self.lang.get_string(15))
            self.default_label = "<span size='large' ><u><i>" + self.lang.get_string(15) + "</i></u></span>\n\n" + self.lang.get_string(16)
            self.status = self.const.get_connectionerror()
            self.label.set_markup(self.default_label)
            self.started = False
            self.show_popup()

    def mail_check(self, event=None):
        # If checking, cancel mail check
        if self.mailcheck:
            print "self.mailcheck"
            return gtk.TRUE
        # If popup is up, destroy it
        if self.popup:
            self.destroy_popup()
        self.mailcheck = True
        print "----------"
        print "checking for new mail (" + time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()) + ")"
        while gtk.events_pending():
            gtk.main_iteration(gtk.TRUE)

        # Get new messages count
        attrs = self.has_new_messages()

        # If mail check was unsuccessful
        if attrs[0] == -1:
            self.mailcheck = False
            return gtk.TRUE

        if attrs[1] > 0:
            print str(attrs[1]) + " new messages"
            sender = attrs[2]
            subject = attrs[3]
            snippet = attrs[4]
            if len(snippet) > 0:
                self.default_label = "<span size='large' ><u><i>" + self.lang.get_string(17) + sender[0: 24] + "</i></u></span>\n" + shortenstring(subject, 20)  # +"\n\n"+snippet+"..."
            else:
                self.default_label = "<span size='large' ><u><i>" + self.lang.get_string(17) + sender[0: 24] + "</i></u></span>\n" + shortenstring(subject, 20)  # +"\n\n"+snippet+"..."
            self.show_popup()
        if attrs[0] > 0:
            print str(attrs[0]) + " unread messages"
            s = ' '
            if attrs[0] > 1:
                s = self.lang.get_string(35) + " "
            self.tray.set_tooltip_text((self.lang.get_string(19)) % {'u': attrs[0], 's': s})
            pixbuf = gtk.gdk.pixbuf_new_from_file(ICON2_PATH)
        else:
            print "no new messages"
            self.default_label = "<span size='large' ><i><u>" + self.lang.get_string(21) + "</u></i></span>\n\n\n" + self.lang.get_string(18)
            self.tray.set_tooltip_text(self.lang.get_string(18))
            pixbuf = gtk.gdk.pixbuf_new_from_file(ICON_PATH)

        self.label.set_markup(self.default_label)
        scaled_buf = pixbuf.scale_simple(24, 24, gtk.gdk.INTERP_BILINEAR)
        self.tray.set_from_pixbuf(scaled_buf)
        self.unreadmsgcount = attrs[0]
        self.mailcheck = False
        return gtk.TRUE

    def has_new_messages(self):
        unreadmsgcount = 0
        # Get total messages in inbox
        try:
            self.connection.refreshInfo()
            unreadmsgcount = self.connection.getUnreadMsgCount()
        except:
            # If an error ocurred, cancel mail check
            print "getUnreadMsgCount() failed, will try again soon"
            return (-1,)

        sender = ''
        subject = ''
        snippet = ''
        finalsnippet = ''
        if unreadmsgcount > 0:
            # Get latest message data
            sender = self.connection.getMsgAuthorName(0)
            subject = self.connection.getMsgTitle(0)
            snippet = self.connection.getMsgSummary(0)
            if len(sender) > 12:
                finalsnippet = shortenstring(snippet, 20)
            else:
                finalsnippet = shortenstring(snippet, 40)
        # Really new messages? Or just repeating...
        newmsgcount = unreadmsgcount - self.unreadmsgcount
        self.unreadmsgcount = unreadmsgcount
        if unreadmsgcount > 0:
            return (unreadmsgcount, newmsgcount, sender, subject, finalsnippet)
        else:
            return (unreadmsgcount, 0, sender, subject, finalsnippet)

    def show_popup(self):
        # If popup is up, destroy it
        if self.popup:
            self.destroy_popup()
        # Generate popup
        print "generating popup"
        self.popuptimer = gtk.timeout_add(self.options['animationdelay'], self.popup_proc)
        self.window.show()
        return

    def destroy_popup(self):
        print "destroying popup"
        if self.popuptimer > 0:
            gtk.timeout_remove(self.popuptimer)
        if self.waittimer > 0:
            gtk.timeout_remove(self.waittimer)
        self.senddown = False
        self.hassettimer = 0
        self.window.hide()
        self.window.resize(180, 1)
        self.window.move(gtk.gdk.screen_width() - self.width, gtk.gdk.screen_height() - self.height)
        return

    def popup_proc(self):
        # Set popup status flag
        if not self.popup:
            self.popup = True
        currentsize = self.window.get_size()
        currentposition = self.window.get_position()
        positiony = currentposition[1]
        sizey = currentsize[1]
        if self.senddown:
            if sizey < 2:
                # If popup is down
                self.senddown = False
                self.window.hide()
                self.window.resize(180, 1)
                self.window.move(gtk.gdk.screen_width() - self.width, gtk.gdk.screen_height() - self.height)
                self.popup = False
                return gtk.FALSE
            else:
                # Move it down
                self.window.resize(180, sizey - 2)
                self.window.move(gtk.gdk.screen_width() - self.width, positiony + 2)
        else:
            if sizey < 140:
                # Move it up
                self.window.resize(180, sizey + 2)
                self.window.move(gtk.gdk.screen_width() - self.width, positiony - 2)
            else:
                # If popup is up, run wait timer
                self.popup = True
                if self.hassettimer == 0:
                    self.waittimer = gtk.timeout_add(self.options['popuptimespan'], self.wait)
                    self.hassettimer = 1
        return gtk.TRUE

    def wait(self):
        self.senddown = True
        self.hassettimer = 0
        return gtk.FALSE

    def tray_icon_clicked(self, signal, event):
        if event.button == 3:
            #self.popup_menu = notifierpopup.GmailPopupMenu(self)
            self.popup_menu.show_menu(event)
        else:
            self.label.set_markup(self.default_label)
            self.show_popup()

    def event_box_clicked(self, signal, event):
        if event.button == 1:
            self.gotourl()

    def exit(self, event):
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, self.lang.get_string(5))
        dialog.width, dialog.height = dialog.get_size()
        dialog.move(gtk.gdk.screen_width() / 2 - dialog.width / 2, gtk.gdk.screen_height() / 2 - dialog.height / 2)
        ret = dialog.run()
        if(ret == gtk.RESPONSE_YES):
            gtk.main_quit(0)
        dialog.destroy()

    def gotourl(self, wg=None):
        print "----------"
        print "launching browser " + self.options['browserpath'] + " http://gmail.google.com"
        os.system(self.options['browserpath'] + " http://gmail.google.com &")

    def update_config(self, event=None):
        # Kill all timers
        if self.popup:
            self.destroy_popup()
        if self.started:
            gtk.timeout_remove(self.maintimer)
        # Run the configuration dialog
        self.configWindow.show()

        # Update user/pass
        self.connection = notifieratom.GmailAtom(self.options["gmailusername"], self.options["gmailpassword"])
        self.connect()
        self.popup_menu = notifierpopup.GmailPopupMenu(self)
        if not self.mailcheck:
            self.show_popup()

        # Update popup location
        self.window.resize(180, 1)
        self.width, self.height = self.window.get_size()
        self.height += self.options["voffset"]
        self.width += self.options["hoffset"]
        self.window.move(gtk.gdk.screen_width() - self.width, gtk.gdk.screen_height() - self.height)

        # Update language
        self.lang = self.configWindow.get_lang()

        # Update popup menu
        self.popup_menu = notifierpopup.GmailPopupMenu(self)
        return

    def main(self):
        gtk.main()

if __name__ == "__main__":
    warnings.filterwarnings(action="ignore", category=DeprecationWarning)
    gmailnotifier = GmailNotify()
    gmailnotifier.main()
