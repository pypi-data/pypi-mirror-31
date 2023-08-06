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

**Attention** Il est nécessaire d'avoir une connection internet pour utiliser pip et lors du premier lancement de l'application. Des fichiers doivent être téléchargés depuis internet.

Pour afficher l'aide, la commande suivante est diponible

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
