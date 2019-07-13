# USBGuard GNOME user interface

## Requirements

### USBGuard

Requires USBGuard to run. https://usbguard.github.io/.
Needs basic configuration after installation.
### Installation

Check out project repository and install system-wide:
```
git clone https://github.com/6E006B/usbguard-gnome.git .
python -m compileall usbguard-gnome
sudo cp -r usbguard-gnome /opt
sudo cp /opt/usbguard-gnome/usbguard* /usr/share/applications/
```

Initialize settings:
```
sudo cp /opt/usbguard-gnome/src/org.gnome.usbguard.gschema.xml /usr/share/glib-2.0/schemas
sudo glib-compile-schemas /usr/share/glib-2.0/schemas
``` 

Open `USBGuard` or `USBGuard Applet` from the menu.
You may want to add `USBGuard Applet` to the autostarting applications.

### Configuration

A simple GUI solution to change the settings is dconf-editor.
Here change the values to be found at org.gnome.usbguard.

## Development

### Internationalisation (I18N)

Two bash scripts support I18N:

#### extract_strings.sh

Will extract strings in python code into a *.pot* file

#### generate_mo.sh

Will generate a compiled *.mo* files out of translated *.po* files

## Programs

This package contains

## usbguard_gnome_window.py

Display a management window for your usb devices. Requires the user to have rights to modify the usbguard policy

## usbguard_gnome_applet.py

An applet for GNOME
