#!/bin/bash

#
# Take translated file and convert to binary .mo format

mkdir -p mo/de_DE.UTF-8/LC_MESSAGES/
msgfmt i18n/de.po -o mo/de_DE.UTF-8/LC_MESSAGES/usbguard_gnome.mo

mkdir -p mo/en_US.UTF-8/LC_MESSAGES/
msgfmt i18n/en.po -o mo/en_US.UTF-8/LC_MESSAGES/usbguard_gnome.mo

mkdir -p mo/sl_SI.UTF-8/LC_MESSAGES/
msgfmt i18n/sl.po -o mo/sl_SI.UTF-8/LC_MESSAGES/usbguard_gnome.mo

