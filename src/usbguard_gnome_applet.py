from __future__ import absolute_import, print_function, unicode_literals

import gi
import signal

gi.require_version('AppIndicator3', '0.1')
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')
from gi.repository import AppIndicator3, Gtk, Notify

from src.new_device_window import USBGuardNewDeviceApplication
from src.usbguard_dbus import USBGuardDBUS
from src.usbguard_gnome_window import USBGuardGnomeApplication

# Gdk.threads_init()
APPINDICATOR_ID = 'USBGuardGnomeApplet'


class USBGuardAppIndicator(object):

    usbguard_app = None

    def __init__(self):
        Notify.init(APPINDICATOR_ID)
        self.indicator = AppIndicator3.Indicator.new(
            APPINDICATOR_ID,
            '/home/chriz/repositories/usbguard/src/GUI.Qt/resources/usbguard-icon.svg',
            AppIndicator3.IndicatorCategory.SYSTEM_SERVICES
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.update_menu()
        self.usbguard_dbus = USBGuardDBUS.get_instance()
        self.usbguard_dbus.register_device_policy_changed_callback(self.new_device_callback)

    def new_device_callback(self, device):
        app = USBGuardNewDeviceApplication(device, self.usbguard_dbus)
        app.run()

    def run(self):
        Gtk.main()
        print("Gtk.main() returned")

    def update_menu(self):
        menu = Gtk.Menu()
        open_text = 'Open' if self.usbguard_app is None else 'Close'
        item_open = Gtk.MenuItem(open_text)
        item_open.connect('activate', self.on_open)
        menu.append(item_open)
        item_quit = Gtk.MenuItem('Quit')
        item_quit.connect('activate', self.on_quit)
        menu.append(item_quit)
        menu.show_all()
        self.indicator.set_menu(menu)

    def open_window(self):
        self.execute_open_window()
        # Notify.Notification.new("USBGuard Applet", "message", None).show()

    def quit(self):
        Notify.uninit()
        Gtk.main_quit()

    def execute_open_window(self):
        if self.usbguard_app is None:
            self.usbguard_app = USBGuardGnomeApplication()
            self.usbguard_app.run()
        else:
            self.usbguard_app.quit()
            self.usbguard_app = None
        self.update_menu()

    def on_quit(self, _):
        if self.usbguard_app is not None:
            self.usbguard_app.quit()
        self.quit()

    def on_open(self, _):
        self.open_window()


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    USBGuardAppIndicator().run()

if __name__ == "__main__":
    main()
