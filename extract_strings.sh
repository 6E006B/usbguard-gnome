#!/bin/bash
#
# Create basic translation file

pybabel extract -k _ -o i18n/en.pot src/*.py

cd i18n
msginit --locale=en --input=en.pot
msginit --locale=de --input=en.pot
msginit --locale=sl --input=en.pot
cd ..
