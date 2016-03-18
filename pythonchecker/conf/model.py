"""config/model.py

Store the plugin classes which handle the plugin's configuration file.
"""

import os
import json


class Configuration(object):
    """Interface to handle the database of preferences."""

    JSON_FOLDER = os.path.dirname(os.path.realpath(__file__))
    JSON_NAME = "configurator.json"
    JSON_PATH = os.path.join(JSON_FOLDER, JSON_NAME)

    def __init__(self):
        """Return a new instance of CheckerConfigurator."""

        self.dict = {"General": {}, "Pep8": {}, "PyLint": {}}
        if not os.path.exists(self.JSON_PATH):
            with open(self.JSON_PATH, "w") as json_file:
                pass
        else:
            with open(self.JSON_PATH, "r") as json_file:
                try:
                    self.dict = json.load(json_file)
                except ValueError:
                    pass

    def load(self, key):
        """Return the preferences for a specific checker."""

        try:
            out = self.dict[key]
            if isinstance(out, dict):
                return out
        except KeyError:
            pass

    def push(self):
        """Update the preferences within the database."""

        with open(self.JSON_PATH, "w") as json_file:
            json.dump(self.dict, json_file, indent=4)

