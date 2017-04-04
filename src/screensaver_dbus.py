# -*- coding: utf8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import dbus
from dbus.mainloop.glib import DBusGMainLoop


class ScreensaverDBUS(object):

    INSTANCE = None

    @classmethod
    def get_instance(cls):
        if cls.INSTANCE is None:
            cls.INSTANCE = ScreensaverDBUS()
        return cls.INSTANCE

    def __init__(self):
        DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SessionBus()
        screensaver_object = self.bus.get_object('org.gnome.ScreenSaver', '/org/gnome/ScreenSaver')
        self.screensaver_interface = dbus.Interface(screensaver_object, dbus_interface='org.gnome.ScreenSaver')
        self.add_signal_receivers()
        self.screensaver_active_changed_callbacks = []

    def add_signal_receivers(self):
        self.screensaver_interface.connect_to_signal('ActiveChanged', self.on_screensaver_active_changed)

    def on_screensaver_active_changed(self, active):
        for callback in self.screensaver_active_changed_callbacks:
            callback(active)

    def register_screensaver_active_changed_callback(self, callback):
        self.screensaver_active_changed_callbacks.append(callback)

    def unregister_screensaver_active_changed_callback(self, callback):
        self.screensaver_active_changed_callbacks.remove(callback)