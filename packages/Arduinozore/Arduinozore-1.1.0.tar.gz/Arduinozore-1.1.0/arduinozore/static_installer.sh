#!/bin/sh

echo "Installing static files..."
#semantic
cd ~/.arduinozore/static >/dev/null 2>/dev/null
wget https://github.com/Semantic-Org/Semantic-UI-CSS/archive/master.zip -O semantic.zip >/dev/null 2>/dev/null
unzip semantic.zip >/dev/null 2>/dev/null
mv Semantic-UI-* semantic >/dev/null 2>/dev/null
rm semantic.zip >/dev/null 2>/dev/null

#jquery
wget https://code.jquery.com/jquery-3.3.1.js >/dev/null 2>/dev/null
mv jquery-*.js jquery.js >/dev/null 2>/dev/null

echo "Finished"
