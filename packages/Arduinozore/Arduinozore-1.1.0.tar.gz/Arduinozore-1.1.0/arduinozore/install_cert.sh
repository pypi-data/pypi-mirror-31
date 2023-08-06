#!/bin/bash

echo "Creating ssl certificates..."
cd ~/.arduinozore/certs >/dev/null 2>/dev/null
yes "" | openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout myserver.crt.key -out myserver.crt.pem >/dev/null 2>/dev/null
