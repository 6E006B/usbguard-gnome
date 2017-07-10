# -*- coding: utf8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import sys

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk, Gio, Gtk, Pango

from new_device_window import USBGuardNewDeviceApplication
from usbguard_dbus import USBGuardDBUS


class USBGuardGnomeWindowExpert(Gtk.ApplicationWindow):

    DEVICES_LIST_COLUMNS = [
        'number', 'rule', 'id', 'name', 'port', 'interface', 'description'
    ]

    def __init__(self, app):
        Gtk.ApplicationWindow.__init__(self, title='USBGuard Gnome Window', application=app)

    def init_devices_list(self, devices_list):
        devices_list_model = Gtk.ListStore(int, str, str, str, str, str, str)
        for device in devices_list:
            devices_list_model.append(device.as_list())

        view = Gtk.TreeView(model=devices_list_model)
        for i in range(len(self.DEVICES_LIST_COLUMNS)):
            # cellrenderer to render the text
            cell = Gtk.CellRendererText()
            # # the text in the first column should be in boldface
            # if i == 0:
            #     cell.props.weight_set = True
            #     cell.props.weight = Pango.Weight.BOLD
            # the column is created
            col = Gtk.TreeViewColumn(self.DEVICES_LIST_COLUMNS[i], cell, text=i)
            col.connect('button-press-event', self.on_row_clicked)
            # and it is appended to the treeview
            view.append_column(col)

        # when a row is selected, it emits a signal
        # view.get_selection().connect("changed", self.on_changed)

        # # the label we use to show the selection
        # self.label = Gtk.Label()
        # self.label.set_text("")

        # a grid to attach the widgets
        grid = Gtk.Grid()
        grid.attach(view, 0, 0, 1, 1)
        grid.attach(self.label, 0, 1, 1, 1)

        # attach the grid to the window
        self.add(grid)

class USBGuardGnomeWindow(Gtk.ApplicationWindow):

    DEVICES_LIST_COLUMNS = [
        'number', 'rule', 'id', 'name', 'port', 'interface', 'description'
    ]

    def __init__(self, app):
        Gtk.ApplicationWindow.__init__(self, title='USBGuard Gnome Window', application=app)
        self.application = app

    def init_devices_list(self, devices_list):
        self.devices_list_model = Gtk.ListStore(int, str, str, str, str, str, str)
        for device in devices_list:
            self.devices_list_model.append(device.as_list())

        view = Gtk.TreeView(model=self.devices_list_model)
        for i in range(len(self.DEVICES_LIST_COLUMNS)):
            cell = Gtk.CellRendererText()
            # the text in the first column should be in boldface
            if i == 0:
                cell.props.weight_set = True
                cell.props.weight = Pango.Weight.BOLD
            col = Gtk.TreeViewColumn(self.DEVICES_LIST_COLUMNS[i], cell, text=i)
            view.append_column(col)

        view.connect("button-press-event", self.on_row_clicked)

        grid = Gtk.Grid()
        grid.attach(view, 0, 0, 1, 1)
        self.add(grid)

    def on_row_clicked(self, tree_view, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            # model, treeiter = tree_view.get_selection().get_selected()
            # path, column = tree_view.get_cursor()
            tree_path = tree_view.get_path_at_pos(event.x, event.y)[0]
            # print("right mouse button clicked on: {}".format(model[treeiter][0]))
            # print("iter = {}".format(self.devices_list_model[self.devices_list_model.get_iter(path)][0]))
            print("tree_path = {}".format(self.devices_list_model[self.devices_list_model.get_iter(tree_path)][0]))
            device_number = self.devices_list_model[self.devices_list_model.get_iter(tree_path)][0]
            self.show_entry_popup_menu(event, device_number)

    def show_entry_popup_menu(self, event, device_number):
        menu = Gtk.Menu()
        item_details = Gtk.MenuItem("Details")
        item_details.connect('activate', self.application.on_details_clicked, device_number)
        menu.append(item_details)
        menu.show_all()
        menu.popup(None, None, None, None, event.button, event.time)


class USBGuardGnomeApplication(Gtk.Application):

    APPLICATION_ID = "org.gnome.usbguard.main"

    def __init__(self):
        Gtk.Application.__init__(self, application_id=self.APPLICATION_ID)
        self.usbguard_dbus = USBGuardDBUS.get_instance()
        self.window = None

    def do_activate(self):
        self.window = USBGuardGnomeWindow(self)
        devices_list = self.usbguard_dbus.get_all_devices()
        self.window.init_devices_list(devices_list)
        self.window.show_all()

    def do_startup(self):
        Gtk.Application.do_startup(self)

        # create a menu
        menu = Gio.Menu()
        # append to the menu three options
        menu.append("Quit", "app.quit")
        # set the menu as menu of the application
        self.set_app_menu(menu)

        # option "quit"
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self.on_quit_clicked)
        self.add_action(quit_action)

    def on_quit_clicked(self, action, parameter):\
        self.execute_quit()

    def execute_quit(self):
        print("You have quit.")
        self.window.close()
        self.quit()

    def on_details_clicked(self, widget, device_number):
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
