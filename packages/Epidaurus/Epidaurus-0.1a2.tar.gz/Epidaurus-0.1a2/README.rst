Ἐπίδαυρος [1]_ is a PID based room temperature controller - to be used
in combination with pelops/copreus, pelops/argaeus and pelops/alcathous.

Part of `pelops <https://gitlab.com/pelops/pelops>`__.

For Users
=========

Installation Core-Functionality
-------------------------------

Prerequisites for the core functionality are:

::

    sudo apt install python3 python3-pip
    sudo pip3 install paho-mqtt pyyaml pelops

Install via pip:

::

    sudo pip3 install epidaurus

To update to the latest version add ``--upgrade`` as prefix to the
``pip3`` line above.

Install via gitlab (might need additional packages):

::

    git clone git@gitlab.com:pelops/epidaurus.git
    cd epidaurus
    sudo python3 setup.py install

This will install the following shell scripts: \* ``epidaurus``

The script cli arguments are: \* '-c'/'--config' - config file
(mandatory) \* '-v' - verbose output (optional) \* '--version' - show
the version number and exit

YAML-Config
-----------

A yaml [2]_ file must contain four root blocks: \* mqtt - mqtt-address,
mqtt-port, and path to credentials file mqtt-credentials (a file
consisting of two entries: mqtt-user, mqtt-password) \* controller -
parameters for the controller and the embedded pid

::

    mqtt:
        mqtt-address: localhost
        mqtt-port: 1883
        mqtt-credentials: ~/credentials.yaml

    controller:
        value-idle: 4.5  # idle mode output - heating system does nothing
        value-min: 5  # minimum output for active (=heating) system
        value-max: 23  # maximum value for heater
        pid-max-output: 500  # for normalization purposes. this is the expected maximum output of the pid controller
        idle-mode-threshold: 0.75  # if temperature is this value above set-point, set output to volt-idle value.
        topics-sub:
            set-point: /test/thermostat/set-point
            input:     /test/thermostat/input
        topics-pub:
            output: /test/thermostat/output
        pid:
            p-gain: 75
            i-gain: 20
            d-gain: 0
            update-interval: 30  # in seconds (in fact not used anywhere)
            windup-guard: 20  # protect integral term from windup

systemd
-------

-  add systemd example.

For Developers
==============

Getting Started
---------------

The project consists of two main modules: \* ``pid`` - classic
pid-implementation \* ``controller`` - wraps around the ``pid`` and adds
thermostat related behavior like minimum output, idle output,
normalization of pid output to expected voltage range.

The values for ``pid`` and some for ``controller`` must be determined
using experiments with the real system. To get a first set of parameters
you can use ``tests/test_controller_model_nomqtt.py`` together with
``tools/model_trivial_flat.py``.

Todos
-----

-  Auto parameterization of pid
-  Sanity check of yaml config
-  Automated unit tests
-  ...

Misc
----

The code is written for ``python3`` (and tested with python 3.5 on an
Raspberry Pi Zero with Raspbian Stretch).

`Merge requests <https://gitlab.com/pelops/epidaurus/merge_requests>`__
/ `bug reports <https://gitlab.com/pelops/epidaurus/issues>`__ are
always welcome.

.. [1]
   The icon used for this project is not Epidaurus, son of pelops.

.. [2]
   Currently, pyyaml is yaml 1.1 compliant. In pyyaml On/Off and Yes/No
   are automatically converted to True/False. This is an unwanted
   behavior and deprecated in yaml 1.2. In copreus this autoconversion
   is removed. Thus, On/Off and Yes/No are read from the yaml file as
   strings (see module baseclasses.mypyyaml).

