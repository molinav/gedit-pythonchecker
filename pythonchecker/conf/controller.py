"""config/controller.py

Store the plugin's preferences dialog controller.
"""

from . model import CheckerConfigurator
from . view import CheckerConfiguratorView


class CheckerConfiguratorController(object):
    """Controller for the preferences dialog."""

    def __init__(self):
        """Return a new instance of CheckerConfiguratorController."""

        # Load options from json file and preferences dialog.
        self.database = CheckerConfigurator()
        self.view = CheckerConfiguratorView()

        for page in self.view.get_children():

            if page.name == "General":
                # Get property "location".
                db_g = self.database.load(page.name)
                try:
                    db_g["location"]
                except KeyError:
                    db_g["location"] = 0
                # Set page elements.
                page.combo_location.set_active(db_g["location"])
                page.combo_location.connect(
                    "changed", self.on_combo_location_changed)
            else:
                # Get property "enable".
                db_c = self.database.load(page.name)
                try:
                    db_c["enable"]
                except KeyError:
                    db_c["enable"] = False
                # Set page elements.
                page.check_enable.set_active(db_c["enable"])
                page.check_enable.connect(
                    "toggled", self.on_check_enable_toggled)

        # Create handlers.
        self.view.connect("destroy", self.on_closed)

    def on_closed(self, *args):
        """Handler triggered when the preferences dialog is closed."""

        self.database.push()

    def on_check_enable_toggled(self, check_enable):
        """Handler triggered when the enable check is toggled."""

        page = check_enable.get_parent()
        db_c = self.database.load(page.name)
        db_c["enable"] = not db_c["enable"]

    def on_combo_location_changed(self, combo_location):
        """Handler triggered when the enable check is toggled."""

        page = combo_location.get_parent().get_parent()
        db_g = self.database.load(page.name)
        # Update property "location".
        active_iter = combo_location.get_active_iter()
        db_g["location"] = combo_location.get_model()[active_iter][0]

