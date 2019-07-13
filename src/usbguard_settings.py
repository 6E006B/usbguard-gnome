import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gio


class USBGuardSettings(Gio.Settings):

    def __init__(self):
        super(USBGuardSettings, self).__init__('org.gnome.usbguard')

    def get_hid_screenlock(self):
        return self.get_boolean('hid-screenlock')

    def get_hid_screenlock_timeout(self):
        return self.get_int('hid-screenlock-timeout')

    def get_notification_timeout(self):
        return self.get_int('notification-timeout')

    def get_detailed_view(self):
        return self.get_boolean('detailed-view')
