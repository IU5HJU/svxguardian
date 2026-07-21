"""
Lettura della configurazione di SvxLink.
"""

import configparser
from pathlib import Path


DEFAULT_CONFIG = "/etc/svxlink/svxlink.conf"


class SvxConfig:

    def __init__(self, filename=DEFAULT_CONFIG):

        self.filename = filename
        self.config = configparser.ConfigParser()

    def load(self):

        if not Path(self.filename).exists():
            raise FileNotFoundError(self.filename)

        self.config.read(self.filename)

    def get(self, section, option, fallback=None):

        return self.config.get(section, option, fallback=fallback)
