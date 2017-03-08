from __future__ import absolute_import, print_function, unicode_literals

import sys

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk, Pango

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


        grid = Gtk.Grid()
        grid.attach(view, 0, 0, 1, 1)
        self.add(grid)


class USBGuardGnomeApplication(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self)
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
        quit_action.connect("activate", self.quit_cb)
        self.add_action(quit_action)

    def quit_cb(self, action, parameter):
        print("You have quit.")
        self.quit()


def main():
    app = USBGuardGnomeApplication()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)

if __name__ == "__main__":
    main()
