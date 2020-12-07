#! /usr/bin/env python
# -*- coding: utf-8 -*-

# __init__.py
#
# Copyright (C) 2010 - xulong <fangkailove@gmail.com>
#


import rhythmdb, rb
import gobject
import gtk
import GoogleMusicProxy
from GMusicSource import GMusicSource
import webbrowser

class GMusicEntryType(rhythmdb.EntryType):
    def __init__(self):
        rhythmdb.EntryType.__init__(self, name='gmusic')

    def can_sync_metadata(self, entry):
        return True


class GMusicPlugin(rb.Plugin):
    #
    # Core methods
    #

    def __init__(self):
        rb.Plugin.__init__(self)

    def activate(self, shell):
        self.db = shell.get_property("db")

        self.entry_type = GMusicEntryType()
        self.db.register_entry_type(self.entry_type)

        width, height = gtk.icon_size_lookup(gtk.ICON_SIZE_LARGE_TOOLBAR)
        icon = gtk.gdk.pixbuf_new_from_file_at_size(self.find_file("google.png"), width, height)

        group = rb.rb_source_group_get_by_name ("stores")
        self.source = gobject.new (GMusicSource,
                shell=shell,
                entry_type=self.entry_type,
                plugin=self,
                icon=icon,
                source_group=group)
        shell.register_entry_type_for_source(self.source, self.entry_type)
        shell.append_source(self.source, None) # Add the source to the list



        # Add button
        manager = shell.get_player().get_property('ui-manager')

    	action = gtk.Action('browse_music', _('_search'),
    			_("open the google music webpage"),
    			'gtk-properties')
        action.connect('activate',lambda a: self.browse_music() )
    	self.action_group = gtk.ActionGroup('GMusicPluginActions')
    	self.action_group.add_action(action)

        manager.insert_action_group(self.action_group, 0)
        manager.ensure_update()

        


    def deactivate(self, shell):
        manager = shell.get_player().get_property('ui-manager')

        manager.remove_action_group(self.action_group)
        self.action_group = None

        GoogleMusicProxy.saveList()

        self.db.entry_delete_by_type(self.entry_type)
        self.db.commit()
        self.db = None
        self.entry_type = None

        self.source.delete_thyself()
        self.source = None

    def create_configure_dialog(self, dialog=None):
    	return dialog

        

    def browse_music(self):
        try:
            webbrowser.open_new_tab("http://localhost:52099/music/homepage")
        except:
            webbrowser.open_new_tab("http://localhost:52099/music/homepage")

