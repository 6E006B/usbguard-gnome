# USBGuard GNOME user interface

## Requirements

### USBGuard

Requires USBGuard to run. https://usbguard.github.io/.
Needs basic configuration after installation.

### Dependencies

Debian:

```sudo apt-get install gir1.2-appindicator3-0.1 python-gobject```

Python:

```pip install pygobject pyparsing```

### Installation

Check out project repository and install system-wide:
```
git clone https://github.com/6E006B/usbguard-gnome.git
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

#### DBus PolicyKit Authentication

The default PolicyKit configuration of USBGuard will require the authentication for most interactions.
To permit actions for the local active user, who is member of the `plugdev` group, create an appropriate configuration in `/etc/polkit-1/localauthority.conf.d/52-usbguard.pkla` (for Debian):
```
[Allow active user in plugdev group to control USBGuard]
Action=org.usbguard.Policy1.appendRule;org.usbguard.Policy1.removeRule;org.usbguard.Devices1.applyDevicePolicy;org.usbguard1.setParameter
Identity=unix-group:plugdev
ResultActive=yes
```

To require authentication, but have it cached for a short while use `ResultActive=auth_self_keep` instead of `ResultActive=yes`.

Alternatively you can change the usbguard policy directly (`/usr/share/polkit-1/actions/org.usbguard1.policy`) and change `auth_admin` to `yes` or `auth_self_keep`, depending on your preference.

After changing the policy, restart polkit to use the new version, e.g.: `systemctl restart polkit.service`

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
