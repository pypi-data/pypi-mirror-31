Les différentes étapes sont tirées directement des messages de commit Git.
Elles sont présentées de la plus récente à la plus ancienne.

2018-05-03 19:29:11
-------------------

Updated doc

2018-04-30 09:08:51
-------------------

Added doc + little fix



- Moved arduino code to another folder

- Completed french part of readme

2018-04-27 11:01:52
-------------------

Fixes for raspbery plateform.



- Updated Arduinos recognition from serial ports.

- Deleted a few useless "print".

2018-04-16 08:52:03
-------------------

Added semantic installer in setup

2018-04-16 08:39:24
-------------------

Updated README

2018-04-15 18:06:00
-------------------

Added python3.4 & 3.5 support



- Corrected errors

- Added test for travis

- Plus a few fixes

2018-04-13 11:35:48
-------------------

Enabled Travis and made a bit of cleaning

2018-03-23 13:24:46
-------------------

Added command line parser



- Added an introduction message

- Added creation of config folder

- Made a bit of cleaning too

- Added setup

2018-03-16 13:13:58
-------------------

Added digital port toggling.



- You can now toggle a port by clicking on the corresponding button.

2018-03-12 10:27:03
-------------------

Added sensors and cards



- Added model, view(template), controller(Handler) for sensors and cards.

2018-03-09 06:07:24
-------------------

Major update



- Added index page that lists connected devices

- Added table for viewing sensors values in device page

- Added a serial manager to manager sensor readers (avoids multiple opening of serial ports which raises an error)

- Added subprocesses for reading serial ports

2018-03-06 08:13:40
-------------------

[structure] Refonte majeur



- La partie web du projet est maintenant plus hierarchisée donc moins brouillon.

- Structure:

- - Un dossier pour les handlers

- - Un dossier static pour les assets (semantic installable via le script semantic_installer.sh)

- - Un dossier pours les templates

- - Un fichier main qui lance le serveur

- - Un fichier qui contient les capteurs (à voir comment on fait dans le futur)

- - Un fichier de config

- - Un fichier d'urls

2018-02-23 14:03:02
-------------------

Project base



- Still a lot of shit to clean.. Sorry for this..

2018-02-23 13:52:04
-------------------

Initial commit
