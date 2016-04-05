"""config/controller.py

Store the plugin's preferences dialog controller.
"""

from . model import Configuration
from . view import View


class Controller(object):
    """Controller for the preferences dialog."""

    def __init__(self):
        """Run when creating a new instance of Controller."""

        # Load options from json file and preferences dialog.
        self.conf = Configuration()
        self.view = View()

        for page in self.view.get_children():

            if page.name == "General":
                # Get property "location".
                db_g = self.conf.load(page.name)
                try:
                    db_g.location
                except AttributeError:
                    db_g.location = True
                # Set page elements.
                page.combo_location.set_active(db_g.location)
                page.combo_location.connect(
                    "changed", self.on_combo_location_changed)
            else:
                # Get property "enable".
                db_c = self.conf.load(page.name)
                try:
                    db_c.enable
                except AttributeError:
                    db_c.enable = True
                # Set page elements.
                page.check_enable.set_active(db_c.enable)
                page.check_enable.connect(
                    "toggled", self.on_check_enable_toggled)

        # Create handlers.
        self.view.connect("destroy", self.on_close)

    def on_check_enable_toggled(self, check_enable):
        """Trigger when the enable check is toggled."""

        page = check_enable.get_parent()
        db_c = self.conf.load(page.name)
        db_c.enable = not db_c.enable

    def on_close(self, *args):
        """Trigger when the preferences dialog is closed."""

        self.conf.save()
        self.conf = None

    def on_combo_location_changed(self, combo_location):
        """Trigger when the combobox for location is changed."""

        page = combo_location.get_parent().get_parent()
        db_g = self.conf.load(page.name)
        # Update property "location".
        active_iter = combo_location.get_active_iter()
        db_g.location = combo_location.get_model()[active_iter][0]

