"""Tools packages."""

import os

from arduinozore.settings import DEVICE_CONFIG_FOLDER
from arduinozore.settings import path
from serial.tools import list_ports
from yaml import safe_load


def get_arduinos():
    """Return connected arduinos devices."""
    serials = list(list_ports.comports())
    return [s for s in serials if 'Arduino' in s.description or (
        s.manufacturer is not None and 'Arduino' in s.manufacturer)]


def get_arduino(name):
    """Return arduino by name."""
    arduinos = get_arduinos()
    arduino = next(
        (arduino for arduino in arduinos if name in arduino.device), None)
    return arduino


def load_config(config_file):
    """Load port list from specific config file."""
    with open(config_file, 'r') as f:
        datas = safe_load(f)
    ports = {k: datas['ports'][k]
             for k in datas['ports'] if len(datas['ports'][k]) is not 0}
    return (datas['device_name'], ports)


def load_config_from_arduino(arduino):
    """Load port list corresponding to arduino if it exists."""
    filenames = os.listdir(DEVICE_CONFIG_FOLDER)
    config_name = get_config_name(arduino)
    config_file = path(DEVICE_CONFIG_FOLDER, config_name)
    if config_name in filenames:
        return load_config(config_file)
    else:
        return (None, None)


def get_config_name(arduino):
    """Return config filename for arduino."""
    config_name = str(arduino.vid)
    config_name += str(arduino.pid)
    config_name += str(arduino.serial_number)
    config_name += ".yaml"
    return config_name
