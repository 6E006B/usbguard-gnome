# USBGuard GNOME user interface

## Requirements

### USBGuard

Requires USBGuard to run. https://usbguard.github.io/.
Needs basic configuration after installation.
### Installation

```
mkdir /tmp/usbguard
cd /tmp/usbguard/
git clone https://github.com/6E006B/usbguard-gnome.git .
cd /tmp/usbguard/src
python -m compileall .
sudo mkdir /opt/usbguard
sudo cp -r /tmp/usbguard /opt/usbguard/
sudo cp /opt/usbguard/usbguard* /usr/share/applications/
``` 
Open USBGUARD or USBGUARD Applet from the menu.
You may want to add USBGUARD Applet to the autostarting applications.


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
