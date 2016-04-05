"""config/model.py

Store the plugin classes which handle the plugin's configuration file.
"""

import os
import json
 

class Dictionary(object):
    """Generic object which can import and export attributes using dicts."""

    VALID_TYPES = (str, bool, int, float)

    def __init__(self, dictionary=None):
        """Run when creating a new Dictionary instance."""

        if dictionary is None:
            self.from_dict({})
        elif isinstance(dictionary, dict):
            self.from_dict(dictionary)
        else:
            msg = "type for input argument must be dict"
            raise TypeError(msg)

    def __str__(self):
        """Print str version of the Dictionary instance."""

        return str(self.to_dict())

    def from_dict(self, dictionary):
        """Import attributes from a dictionary."""

        out = {}
        for key, val in dictionary.items():
            if not isinstance(key, str):
                msg = "key '{}' is not a str".format(key)
                raise TypeError(msg)
            if isinstance(val, dict):
                out[key] = Dictionary(val)
            elif isinstance(val, self.VALID_TYPES):
                out[key] = val
            else:
                msg = "value type for '{}' is not valid".format(key)
                raise TypeError(msg)
        self.__dict__ = out

    def to_dict(self):
        """Export attributes into a dictionary."""

        out = {}
        for key, val in self.__dict__.items():
            if isinstance(val, Dictionary):
                out[key] = val.to_dict()
            elif isinstance(val, self.VALID_TYPES):
                out[key] = val
            else:
                msg = "value type for '{}' is not valid".format(key)
                raise TypeError(msg)
        return out

    def load(self, key):
        """Return an attribute if Dictionary."""

        out = self.__getattribute__(key)
        if isinstance(out, Dictionary):
            return out
        else:
            msg = "value type for '{}' is not Dictionary".format(key)
            raise TypeError(msg)


class Configuration(Dictionary):
    """Parser for the plugin's configuration file."""

    DEFAULT = {
        "General": {
            "location": True,
        },
        "Pep8": {
            "enable": True,
        },
        "PyLint": {
            "enable": True,
        }
    }

    JSON_FOLD = os.path.expanduser("~/.config/gedit/plugins/pythonchecker")
    JSON_NAME = "config.json"
    JSON_PATH = os.path.join(JSON_FOLD, JSON_NAME)

    def __init__(self):
        """Run when creating a new Configuration instance."""

        super(Configuration, self).__init__()
        self.open()

    def open(self):
        """Open configuration attributes from file into the object."""

        self.from_dict(self.DEFAULT)
        if not os.path.exists(self.JSON_PATH):
            self.save()
        else:
            with open(self.JSON_PATH, "r") as json_file:
                try:
                    self.from_dict(json.load(json_file))
                except ValueError:
                    self.save()

    def save(self):
        """Save configuration attributes from object into the file."""

        if not os.path.exists(self.JSON_FOLD):
            os.makedirs(self.JSON_FOLD)
        with open(self.JSON_PATH, "w") as json_file:
            json.dump(self.to_dict(), json_file, indent=4)

