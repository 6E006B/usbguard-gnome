#!/usr/bin/env python
#  -*- coding: utf8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from dbus.exceptions import DBusException
import sys

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk, Gio, Gtk, Pango

from new_device_window import USBGuardNewDeviceApplication
from usbguard_dbus import Rule, USBGuardDBUS
from usbguard_settings import USBGuardSettings

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
print('Using locale directory: {}'.format(LOCALE_DIR))


class USBGuardGnomeWindow(Gtk.ApplicationWindow):
    """Window class to display the Application main window"""

    DEVICE_LIST_COLUMNS = [
        _('number'), _('enabled?'), _('id'), _('serial'), _('name'), _('port'), _('interface'), _('description'), _('type')
    ]

    def __init__(self, app, detailed=None):
        Gtk.ApplicationWindow.__init__(self, title=_('USBGuard Gnome Window'), application=app)
        self.application = app
        self.settings = USBGuardSettings()
        self.detailed = detailed if detailed is not None else self.settings.get_detailed_view()
        self.device_list_model = None

    def init_device_list(self, device_list):
        """create the gui device list and grid

        device_list: a list of Device objects - will be displayed in the grid
        """
        self.device_list_model = Gtk.ListStore(int, bool, str, str, str, str, str, str, str)
        for device in device_list:
            print(device.as_list())
            self.device_list_model.append(device.as_list())

        device_list_view = Gtk.TreeView(model=self.device_list_model)
        device_list_view.set_grid_lines(Gtk.TreeViewGridLines.HORIZONTAL)
        for i in range(len(self.DEVICE_LIST_COLUMNS)):
            if i == 1:
                cell = Gtk.CellRendererToggle()
                col = Gtk.TreeViewColumn(self.DEVICE_LIST_COLUMNS[i], cell, active=1)
                device_list_view.append_column(col)
                cell.connect("toggled", self.on_toggled)
            else:
                cell = Gtk.CellRendererText()
                # the text in the first column should be in boldface
                if i == 0:
                    cell.props.weight_set = True
                    cell.props.weight = Pango.Weight.BOLD
                col = Gtk.TreeViewColumn(self.DEVICE_LIST_COLUMNS[i], cell, text=i)
                if not self.detailed:
                    if i == 0 or i == 2 or i == 3 or i == 5 or i == 6:
                        # don't show the number, id, serial, port and interface if not in detailed view
                        col.set_visible(False)
                device_list_view.append_column(col)

        device_list_view.connect("button-press-event", self.on_row_clicked)

        grid = Gtk.Grid()
        grid.attach(device_list_view, 0, 0, 1, 1)
        self.add(grid)

    def on_toggled(self, widget, path):
        """Event handler if device is toggled"""
        current_value = self.device_list_model[path][1]
        new_value = not current_value
        if new_value:
            state = "on"
            rule = Rule.ALLOW
        else:
            state = "off"
            rule = Rule.BLOCK
        print("Switch was turned", state)
        try:
            self.application.usbguard_dbus.apply_device_policy(self.device_list_model[path][0], rule, False)
            self.device_list_model[path][1] = new_value
        except DBusException as e:
            print("Error setting device policy: {}".format(e))
            # TODO: force table refresh

    def on_row_clicked(self, tree_view, event):
        """Connects the right-click on a device entry to the event handler"""
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            # model, treeiter = tree_view.get_selection().get_selected()
            # path, column = tree_view.get_cursor()
            tree_path = tree_view.get_path_at_pos(event.x, event.y)[0]
            # print("right mouse button clicked on: {}".format(model[treeiter][0]))
            # print("iter = {}".format(self.device_list_model[self.device_list_model.get_iter(path)][0]))
            print("tree_path = {}".format(self.device_list_model[self.device_list_model.get_iter(tree_path)][0]))
            device_number = self.device_list_model[self.device_list_model.get_iter(tree_path)][0]
            self.show_entry_popup_menu(event, device_number)

    def show_entry_popup_menu(self, event, device_number):
        """Popup menu handler for a device entry

        Creating and showing the menu

        event:
        device_number: (usbguard) number of the device
        """
        menu = Gtk.Menu()
        item_details = Gtk.MenuItem("Details")
        item_details.connect('activate', self.application.on_details_clicked, device_number)
        menu.append(item_details)
        menu.show_all()
        menu.popup(None, None, None, None, event.button, event.time)

    def set_device_list(self, device_list):
        """
        Sets a new device list to be viewed in the device management window.

        :param device_list: List of devices to show
        :return: None
        """
        self.device_list_model.clear()
        for device in device_list:
            self.device_list_model.append(device.as_list())


class USBGuardGnomeApplication(Gtk.Application):

    APPLICATION_ID = "org.gnome.usbguard.main"

    def __init__(self):
        Gtk.Application.__init__(self, application_id=self.APPLICATION_ID)
        self.usbguard_dbus = USBGuardDBUS.get_instance()
        self.window = None

    def do_activate(self):
        """Init window"""
        self.window = USBGuardGnomeWindow(self)
        device_list = self.usbguard_dbus.get_all_devices()
        self.window.init_device_list(device_list)
        self.window.show_all()
        self.register_presence_changes()

    def on_device_presence_changed(self, event, new_device):
        """
        Callback function to handle device presence changes.

        :param event: Type of presence change
        :param new_device: Device object of new device
        :return: None
        """
        device_list = self.usbguard_dbus.get_all_devices()
        self.window.set_device_list(device_list)

    def register_presence_changes(self):
        """
        Registers for device presence changes at USBGuard DBus service.

        :return: None
        """
        self.usbguard_dbus.register_device_presence_changed_callback(self.on_device_presence_changed)

    def do_startup(self):
        """Init the application"""
        Gtk.Application.do_startup(self)

        # create a menu
        menu = Gio.Menu()
        # append to the menu three options
        menu.append(_("Quit"), "app.quit")
        # set the menu as menu of the application
        self.set_app_menu(menu)

        # option "quit"
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self.on_quit_clicked)
        self.add_action(quit_action)

    def on_quit_clicked(self, action, parameter):
        """Simple handler for on-quite click event"""
        self.execute_quit()

    def execute_quit(self):
        """Terminating the application"""
        print("You have quit.")
        self.window.close()
        self.quit()

    def on_details_clicked(self, widget, device_number):
        """OnClick handler for details on one device

        widget: the widget being clicked
        device_number: number of the device selected
        """
        print("on_details_clicked()")
        print("Menu item " + widget.get_name() + " was selected")
        print("rule_number: {}".format(device_number))
        device = self.usbguard_dbus.get_device(device_number)
        app = USBGuardNewDeviceApplication(device, self.usbguard_dbus)
        rule_id = app.run()


def main():
    app = USBGuardGnomeApplication()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)


if __name__ == "__main__":
    main()
