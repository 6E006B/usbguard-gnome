# -*- coding: utf8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import gi
import os
import sys
import signal
import time

gi.require_version('AppIndicator3', '0.1')
# gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')
from gi.repository import AppIndicator3, Gtk, Notify

from new_device_window import USBGuardNewDeviceApplication
from screensaver_dbus import ScreensaverDBUS
from usbguard_dbus import PresenceEvent, Rule, USBGuardDBUS
from usbguard_gnome_window import USBGuardGnomeApplication

import gettext
import locale
from os.path import abspath, dirname, join

# Setup

APP = 'usbguard_gnome'
WHERE_AM_I = abspath(dirname(__file__))
LOCALE_DIR = join(WHERE_AM_I, '..', 'mo')    # Currently we run from the app dir.
# TODO: Fix this path if we install gnome_usbguard system wide

kwargs = {"localedir": LOCALE_DIR}
if sys.version_info[0] > 3:
    # In Python 2, ensure that the _() that gets installed into built-ins
    # always returns unicodes.  This matches the default behavior under
    # Python 3, although that keyword argument is not present in the
    # Python 3 API.
    kwargs['unicode'] = True
gettext.install(APP, **kwargs)
locale.setlocale(locale.LC_ALL, '')
locale.bindtextdomain(APP, LOCALE_DIR)

# For testing the proper path
print(gettext.find(APP, LOCALE_DIR))
print('Applet using locale directory: {}'.format(LOCALE_DIR))



# Gdk.threads_init()
APPINDICATOR_ID = 'org.gnome.usbguard.appindicator'


class USBGuardAppIndicator(object):
    """App indicator to handle usb events"""

    CURRDIR = os.path.dirname(os.path.abspath(__file__))
    USBGUARD_ICON_PATH = os.path.join(CURRDIR, 'usbguard-icon.svg')
    # TODO: Icon is missing, find it

    usbguard_app = None
    notifications = {}
    screensaver_active = False
    new_devices_on_screensaver = set()

    def __init__(self):
        self.device_policy_changed_ids = []

        Notify.init(APPINDICATOR_ID)
        self.indicator = AppIndicator3.Indicator.new(
            APPINDICATOR_ID,
            self.USBGUARD_ICON_PATH,
            AppIndicator3.IndicatorCategory.SYSTEM_SERVICES
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.update_menu()

        self.usbguard_dbus = USBGuardDBUS.get_instance()
        self.usbguard_dbus.register_device_presence_changed_callback(self.new_device_callback)

        self.screensaver_dbus = ScreensaverDBUS.get_instance()
        self.screensaver_dbus.register_screensaver_active_changed_callback(self.screensaver_active_changed_callback)

    def new_device_callback(self, presenceEvent, device):
        """Callback handling new devices

        Creates the notification

        presenceEvent: event type (remove ?)
        device: device object
        """
        print("new_device_callback({})".format(presenceEvent))
        print("Device: {}".format(device.get_class_description_string()))
        if presenceEvent != PresenceEvent.REMOVE.value:
            if self.screensaver_active:
                self.new_devices_on_screensaver.add(device)
            else:
                # TODO: This feature should be opt-in. Add a configuration setting for it.
                if device.is_hid_only():
                    # Activate screensaver
                    notification = Notify.Notification.new("New keyboard attached", "Locking computer now. Enter your password to activate. If you did not attach a keyboard, check your computer for potentially malicious devices.", self.USBGUARD_ICON_PATH)
                    notification.set_category("device.added")
                    notification.show()
                    time.sleep(20)

                    self.screensaver_dbus.lock()
                    self.allow_device(device, temporary=True)
                else:
                    description = device.get_class_description_string()
                    notification = Notify.Notification.new(_("New USB device inserted"), description, self.USBGUARD_ICON_PATH)
                    notification.add_action('allow', 'Allow', self.on_allow_clicked, device)
                    notification.add_action('block', 'Block', self.on_allow_clicked, device)
                    notification.add_action('default', 'default', self.on_notification_clicked, device)
                    notification.set_timeout(Notify.EXPIRES_NEVER) # TODO: maybe make configurable
                    notification.connect('closed', self.on_notification_closed)
                    notification.set_category("device.added")
                    notification.show()
                    self.notifications[notification.props.id] = notification

    def screensaver_active_changed_callback(self, active):
        """Monitoring screen saver status

        Callback for screen saver state changes

        active: new screen saver state
        """
        print("screensaver is now: {}".format(active))
        self.screensaver_active = active
        if not self.screensaver_active and self.new_devices_on_screensaver:
            title = _("{} USB devices connected during absence").format(
                len(self.new_devices_on_screensaver)
            )
            description = ""
            for device in self.new_devices_on_screensaver:
                description += "\n • {} ({})".format(
                    device.get_class_description_string(),
                    device.name
                )
            notification = Notify.Notification.new(title, description, self.USBGUARD_ICON_PATH)
            notification.set_category("device.added")
            notification.show()
            self.new_devices_on_screensaver = set()

    def run(self):
        """start the app"""
        Gtk.main()
        print("Gtk.main() returned")

    def update_menu(self):
        """Create the menu"""
        menu = Gtk.Menu()
        open_text = _('Open') if self.usbguard_app is None else _('Close')
        item_open = Gtk.MenuItem(open_text)
        item_open.connect('activate', self.on_open)
        menu.append(item_open)
        item_quit = Gtk.MenuItem(_('Quit'))
        item_quit.connect('activate', self.on_quit)
        menu.append(item_quit)
        menu.show_all()
        self.indicator.set_menu(menu)

    def open_window(self):
        """Open window event handler"""
        self.execute_open_window()

    def quit(self):
        """lower exit handler"""
        Notify.uninit()
        Gtk.main_quit()

    def execute_open_window(self):
        """Start the usb guard gnome application

        Or terminate it, if it is running.
        """
        if self.usbguard_app is None:
            self.usbguard_app = USBGuardGnomeApplication()
            self.usbguard_app.run()
        else:
            self.usbguard_app.execute_quit()
            self.usbguard_app = None
        self.update_menu()

    def on_quit(self, _):
        """quit event handler"""
        if self.usbguard_app is not None:
            self.usbguard_app.execute_quit()
        self.quit()

    def on_open(self, _):
        """On open event handler"""
        self.open_window()

    def allow_device(self, device, temporary = False):
        """Allow a device.

        device: Device to allow
        temporary: only add temporary and do not store permissions
        """
        rule_id = self.usbguard_dbus.apply_device_policy(device.number, Rule.ALLOW, temporary)
        self.device_policy_changed_ids.append(rule_id)

    def on_allow_clicked(self, notification, action_name, device):
        """Handle device allow click action

        notification: notification to act on
        action_name: not used
        device: device to allow
        """
        print("on_allow_clicked() for device {}".format(device))
        self.allow_device(device)
        self.notifications[notification.props.id] = None

    def block_device(self):
        """Block a device"""
        rule_id = self.usbguard_dbus.apply_device_policy(device.number, Rule.BLOCK, False)
        self.device_policy_changed_ids.append(rule_id)

    def on_block_clicked(self, notification, action_name, device):
        """Handle device block click action

        notification: notification to act on
        action_name: not used
        device: device to block
        """
        print("on_block_clicked()")
        self.block_device(device)
        self.notifications[notification.props.id] = None

    def on_notification_clicked(self, notification, action_name, device):
        """Handle on-click for notifications

        notification: Notification being clicked
        """
        app = USBGuardNewDeviceApplication(device, self.usbguard_dbus)
        rule_id = app.run()
        self.notifications[notification.props.id] = None

    def on_notification_closed(self, notification):
        """Remove closed notification from internal list

        notification: Notification to remove
        """
        self.notifications[notification.props.id] = None


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    USBGuardAppIndicator().run()


if __name__ == "__main__":
    main()
