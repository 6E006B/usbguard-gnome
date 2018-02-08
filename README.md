# USBGuard GNOME user interface

## Requirements

### USBGuard

Requires USBGuard to run. https://usbguard.github.io/ or ```sudo apt install usbguard```.
Needs basic configuration after installation.


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
