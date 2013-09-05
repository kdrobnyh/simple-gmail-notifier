#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Based on the Gmail Notifier project: http://sourceforge.net/projects/gmail-notify/
# Maintainer: Klim Drobnyh <klim.drobnyh@gmail.com>

import pygtk
pygtk.require('2.0')
import bz2
import gtk
import ConfigParser
import logging
import os
import random
from .langsparser import LangsParser


class ConfigWindow(object):

    options = {"gmailusername": None, "gmailpassword": None, "browserpath": "chromium -U", "lang": "English",
               "checkinterval": 20000, "popuptimespan": 5000}
    config = ConfigParser.RawConfigParser()
    langs_parser = None

    def __init__(self, path):
        self.lang_path = path + "resources/langs.xml"
        self.icon_path = path + "resources/icons/notempty.png"
        self.config_path = os.path.expanduser("~/.config/simple-gmail-notifier/notifier.conf")
        self.read_config()
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title(self.lang["config_title"])
        self.window.set_border_width(5)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_modal(gtk.TRUE)
        self.window.set_resizable(gtk.FALSE)
        icon = gtk.gdk.pixbuf_new_from_file(self.icon_path)
        gtk.window_set_default_icon_list(icon)
        self.window.connect("delete_event", self.on_delete)
        # elements = [ [Option Name, String ID, Entry, Label ], ... ]
        self.elements = [
                        ["gmailusername", "config_username", None, None],
                        ["gmailpassword", "config_password", None, None],
                        ["browserpath", "config_browser", None, None],
                        ["checkinterval", "config_check_interval", None, None],
                        ["popuptimespan", "config_popup_time", None, None],
                    ]

        table = gtk.Table(rows=8, columns=2, homogeneous=gtk.FALSE)
        self.window.add(table)

        for i, element in enumerate(self.elements):
            element_name = element[0]

            label = gtk.Label(self.lang[element[1]])
            label.set_alignment(0, 0.5)
            textbox = gtk.Entry(max=0)

            if self.options[element_name] is not None:
                textbox.set_text(str(self.options[element_name]))

            if element_name == "gmailpassword":
                textbox.set_visibility(gtk.FALSE)
                textbox.set_invisible_char('*')

            element[2] = textbox
            element[3] = label

            table.attach(label, 0, 1, i, i + 1, xpadding=2, ypadding=1)
            table.attach(textbox, 1, 2, i, i + 1, xpadding=2, ypadding=1)
            label.show()
            textbox.show()

        alignment = gtk.Alignment(0.5, 0.5, 0.0, 0.0)
        self.save = gtk.CheckButton(label=self.lang["menu_save"])
        alignment.add(self.save)

        if self.options["gmailusername"] is not None and self.options["gmailpassword"] is not None:
            self.save.set_active(gtk.TRUE)
        else:
            self.save.set_active(gtk.FALSE)

        self.save.show()
        table.attach(alignment, 0, 2, 6, 7)
        alignment.show()

        self.lbl_langs = gtk.Label(self.lang["menu_language"])
        self.lbl_langs.set_alignment(0, 0.5)
        self.cbo_langs = gtk.combo_box_new_text()
        self.cbo_langs.connect('changed', self.update_labels)
        for one_lang in self.langs:
            if one_lang == self.options["lang"]:
                self.cbo_langs.prepend_text(one_lang)
            else:
                self.cbo_langs.append_text(one_lang)
        self.cbo_langs.set_active(0)

        table.attach(self.lbl_langs, 0, 1, 5, 6)
        self.lbl_langs.show()
        table.attach(self.cbo_langs, 1, 2, 5, 6, ypadding=5)
        self.cbo_langs.show()

        button = gtk.Button(stock=gtk.STOCK_OK)
        table.attach(button, 0, 2, 7, 8, ypadding=2)
        button.connect("clicked", self.on_ok)
        button.show()
        table.show()

    def show(self):
        self.window.show()
        self.main()

    def hide(self):
        self.window.hide()

    def checkfile(self, path):
        try:
            return open(path)
        except IOError:
            return None

    def ensure_dir(self, f):
        d = os.path.dirname(f)
        if not os.path.exists(d):
            os.makedirs(d)

    def read_config(self):
        logging.info("Reading configuration")
        self.config = ConfigParser.RawConfigParser()
        files = self.config.read(self.config_path)
        if (len(files) == 1):
            self.loaded_config = files[0]
            logging.info("Configuration file opened")
        else:
            self.config.add_section("options")
            logging.info("Configuration file is not exist. Creating...")
        self.loaded_config = self.config_path
        # Check which options are defined and override defaults
        for key in self.options.keys():
            if (self.config.has_option('options', key)):
                if (type(self.options[key]) == int):
                    self.options[key] = self.config.getint('options', key)
                else:
                    self.options[key] = self.config.get('options', key).replace('"', '')
        for key in ("gmailusername", "gmailpassword"):
            if (self.config.has_option('options', key)):
                self.options[key] = bz2.decompress(self.config.get('options', key).decode('base64'))[::2]
        self.langs_parser = LangsParser(self.lang_path)
        self.langs = self.langs_parser.get_langs()
        self.lang = self.langs_parser.get_lang(self.options["lang"])
        logging.info("Configuration read (%s)" % self.loaded_config)

    def get_options(self):
        return self.options

    def on_delete(self, widget, data=None):
        gtk.main_quit()
        self.hide()
        return gtk.TRUE

    def mix(self, value):
        val = str(value)
        length = len(val)
        #res = ""
        #for x in val:
        #    res += x + val[random.randrange(len(val))]
        return "".join([x + val[random.randrange(length)] for x in val])

    def on_ok(self, widget, callback_data=None):
        message = None
        for element in self.elements:
            if (type(self.options[element[0]]) == int):
                try:
                    self.options[element[0]] = int(element[2].get_text())
                except:
                    message = self.lang["config_error_value"] % element[3].get_text()
                    break
            else:
                self.options[element[0]] = element[2].get_text()

        if message:
            logging.info(message)
            dialog = gtk.MessageDialog(buttons=gtk.BUTTONS_OK, type=gtk.MESSAGE_ERROR)
            dialog.set_position(gtk.WIN_POS_CENTER)
            dialog.set_markup(message)
            dialog.run()
            dialog.destroy()
            return

        active_iter = self.cbo_langs.get_active_iter()
        self.options["lang"] = self.cbo_langs.get_model().get_value(active_iter, 0)

        for key in self.options.keys():
            self.config.set("options", key, self.options[key])

        if not self.save.get_active():
            self.config.remove_option("options", "gmailusername")
            self.config.remove_option("options", "gmailpassword")
        else:
            if self.options["gmailusername"]:
                self.config.set("options", "gmailusername", bz2.compress(self.mix(self.options["gmailusername"])).encode('base64')[:-1])
            if self.options["gmailpassword"]:
                self.config.set("options", "gmailpassword", bz2.compress(self.mix(self.options["gmailpassword"])).encode('base64')[:-1])
        try:
            self.ensure_dir(self.loaded_config)
            self.config.write(open(self.loaded_config, 'w'))
        except:
            logging.info("Can't save settings to file!")
            dialog = gtk.MessageDialog(buttons=gtk.BUTTONS_OK, type=gtk.MESSAGE_WARNING)
            dialog.set_position(gtk.WIN_POS_CENTER)
            dialog.set_markup(self.lang["config_error_save"])
            dialog.run()
            dialog.destroy()
            return
        gtk.main_quit()
        self.hide()

    def update_labels(self, combobox=None):
        active_iter = self.cbo_langs.get_active_iter()
        lang_name = self.cbo_langs.get_model().get_value(active_iter, 0)
        self.lang = self.langs_parser.get_lang(lang_name)
        for element in self.elements:
            element[3].set_label(self.lang[element[1]])
        self.lbl_langs.set_label(self.lang["config_language"])
        self.save.set_label(self.lang["config_save"])
        self.window.set_title(self.lang["config_title"])

    def get_lang(self):
        return self.lang

    def get_lang_name(self):
        return self.options["lang"]

    def main(self):
        gtk.main()