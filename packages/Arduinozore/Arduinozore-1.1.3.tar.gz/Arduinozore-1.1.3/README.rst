`Arduinozore`
=============

.. image:: https://travis-ci.org/S-Amiral/arduinozore.svg?branch=master
    :target: https://travis-ci.org/S-Amiral/arduinozore
    :alt: Build status

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: http://doge.mit-license.org
    :alt: MIT License

.. image:: https://img.shields.io/pypi/v/Arduinozore.svg?maxAge=2592000
    :target: https://pypi.org/project/Arduinozore/
    :alt: PyPI - Python Version

.. image:: https://img.shields.io/pypi/pyversions/Arduinozore.svg
    :target: https://pypi.org/project/Arduinozore/
    :alt: PyPI - Python Version


Realization of a web interface allowing to visualize sensors data sent by an arduino on a serial port.

This package can be installed via :code:`pip install arduinozore`.

We are still working on this README.
------------------------------------

Français
--------

L'installation est aisée. Le package se trouvant sur pypi, il suffit de l'installer via la commande

.. code-block:: bash

    pip install arduinozore

Lors du premier lancement, si aucun dossier de configuration n'est trouvé, il est créé.

**Attention** Il est nécessaire d'avoir une connexion internet pour utiliser pip et lors du premier lancement de l'application. Des fichiers doivent être téléchargés depuis internet.

Pour afficher l'aide, la commande suivante est disponible

.. code-block:: bash

    arduinozore --help
    usage: arduinozore [-h] [-hp HTTP_PORT] [-hsp HTTPS_PORT] [-a path]
                   [--newconfig]

    Arduinozore server

    optional arguments:
    -h, --help            show this help message and exit
    -hp HTTP_PORT, --http_port HTTP_PORT
                        Server http port. Default 8000
    -hsp HTTPS_PORT, --https_port HTTPS_PORT
                        Server https port. Default 8001. Used for sockets too.
    -a path, --arduino path
                        Path where arduino source code will be generated.
    --newconfig           Delete actual config and make a new one. Warning.

En cas de problème, il est possible de supprimer la configuration et la regénérer avec la commande

.. code-block:: bash

    arduinozore --newconfig

Il est possible de spécifier les ports http et https. Par défaut les ports 8000 et 8001 sont utilisés. Pour ce faire, les options suivantes sont disponibles

.. code-block:: bash

    arduinozore -hp 80 -hsp 443

Afin de récupérer le script arduino pour pouvoir le flasher, il est possible de l'obtenir avec l'option `-a` en donnant le path cible.

.. code-block:: bash

    arduinozore -a /destination/path/for/arduino/script

Pour lancer l'application, il suffit d'exécuter

.. code-block:: bash

    arduinozore

et de se rendre à l'adresse fournie dans le terminal.

**Attention**, si votre réseau domestique ne possède pas de serveur DNS, il sera nécessaire de remplacer l'adresse du serveur par son adresse IP afin de pouvoir y accéder.

Pour trouver cette adresse IP, la commande suivante suffit.

.. code-block:: bash

    ifconfig

Par exemple, si lors du lancement, la chose suivante est affichée dans la console

.. code-block:: bash

    /############################################################################################\

         #
        # #   #####  #####  #    # # #    #  ####  ######  ####  #####  ######
       #   #  #    # #    # #    # # ##   # #    #     #  #    # #    # #
      #     # #    # #    # #    # # # #  # #    #    #   #    # #    # #####
      ####### #####  #    # #    # # #  # # #    #   #    #    # #####  #
      #     # #   #  #    # #    # # #   ## #    #  #     #    # #   #  #
      #     # #    # #####   ####  # #    #  ####  ######  ####  #    # ######


    \############################################################################################/

    /############################################################################################\

                          Listening on: https://raspberry:8001

mais que vous ne possédez pas de dns, il faudra remplacer le nom "raspberry" par l'adresse IP du Raspberry Pi obtenue grâce à la commande "ifconfig".

Maintenant, il n'y a plus qu'à ouvrir un navigateur, se rendre à l'adresse correcte et effectuer quelques réglages et le tour est joué!

Tout d'abord, le navigateur risque de vous dire que le certificat n'a pas pu être vérifié. Étant donné qu'il est généré par l'application, il est autosigné. Il suffit donc de l'accepter tel quel.

Dès lors, la page d'accueil du site apparaît. Si des Arduinos sont connectés, il sont listés.

À présent, il est nécessaire de créer une configuration de carte en fonction du type d'Arduino que vous possédez. Cette création peut être atteinte dans les réglages.

Ensuite, il est nécessaire de configurer le ou les capteurs utilisés de la même manière que la ou les cartes.

Il est maintenant possible de configurer l'Arduino et d'interagir avec lui! Bravo!
