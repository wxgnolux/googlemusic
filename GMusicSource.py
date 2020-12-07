#! /usr/bin/env python
# -*- coding: utf-8 -*-

# GMusicSource.py
#
# Copyright (C) 2010 - xulong <fangkailove@gmail.com>
#

import rb, rhythmdb

import os
import gobject
import gtk
import gnome, gconf
import gnome.ui
import xml
import gzip
import datetime
import webbrowser
import threading
import GoogleMusicProxy


class GMusicSource(rb.BrowserSource):
    __gproperties__ = {
            'plugin': (rb.Plugin, 'plugin', 'plugin', gobject.PARAM_WRITABLE|gobject.PARAM_CONSTRUCT_ONLY),
            }

    def __init__(self):

        rb.BrowserSource.__init__(self, name=_("Google music")) #  as a item for the  library tree 

        # catalogue stuff
        self.db = None
        self.__activated = False



    def do_set_property(self, property, value):
        if property.name == 'plugin':
            self.__plugin = value
        else:
            raise AttributeError, 'unknown property %s' % property.name

    def do_impl_get_browser_key (self):
        return "/apps/rhythmbox/plugins/gmusic/show_browser"

    def do_impl_get_paned_key (self):
        return "/apps/rhythmbox/plugins/gmusic/paned_position"

    def do_impl_can_delete (self):
        return False

    def do_impl_pack_paned (self, paned):
        self.__paned_box = gtk.VBox(False, 5)
        self.pack_start(self.__paned_box)
        self.__paned_box.pack_start(paned)

    #
    # RBSource methods
    #

    def do_impl_get_ui_actions(self):
    	return ["browse_music"]


    def do_impl_get_status(self):
        return ("status info", None, None)

    def do_impl_activate(self):
        if not self.__activated:
            shell = self.get_property('shell')
            self.db = shell.get_property('db')
            self.entry_type = self.get_property('entry-type')

            self.__activated = True
            GoogleMusicProxy.bs = self
            ws = webserver(self)
            ws.start()        
            GoogleMusicProxy.loadList()
        rb.BrowserSource.do_impl_activate (self)

    def do_impl_delete_thyself(self):
        rb.BrowserSource.do_impl_delete_thyself (self)



class webserver(threading.Thread):
    def __init__(self,bs):
        threading.Thread.__init__(self)
        self.BrowserSource = bs
    def run(self):
        httpd = GoogleMusicProxy.ThreadingHTTPServer(('localhost', 52099), GoogleMusicProxy.GoogleMusicProxyHandler )
        httpd.serve_forever()

gobject.type_register(GMusicSource)

