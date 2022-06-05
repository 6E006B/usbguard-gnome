#!/bin/bash
#
# Create basic translation file

pybabel extract -k _ -o i18n/en.pot src/*.py

cd i18n
msgmerge -U en.po en.pot
msgmerge -U de.po en.pot
msgmerge -U sl.po en.pot
cd ..
