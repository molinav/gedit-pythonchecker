"""Gedit Python Checker Plugin"""

from . main.controller import CheckerController


class WindowActivatable(CheckerController):
    """Plugin class."""

    def do_activate(self):
        """Run in order to enable the plugin."""

        self.enable()

    def do_deactivate(self):
        """Run in order to disable the plugin."""

        self.disable()

    def do_update_state(self):
        """Run in case of state update."""

        pass

    def do_create_configure_widget(self):
        """Return preferences dialog."""

        return self.configure()

