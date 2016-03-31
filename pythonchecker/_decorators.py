"""_decorators.py

Auxiliary decorators for plugin methods.
"""

from threading import Thread
from gi.repository import GLib


def threaded_with_python(func):
    """Send function into a new thread managed by Python."""

    def wrapper(self, *args, **kwargs):
        """Function wrapper."""

        def inner():
            """Function inside wrapper."""
            return func(self, *args, **kwargs)

        thread = Thread(target=inner)
        thread.daemon = True
        thread.start()

    return wrapper


def threaded_with_glib(func):
    """Send function into a new thread managed by GLib."""

    def wrapper(self, *args, **kwargs):
        """Function wrapper."""

        def inner():
            """Function inside wrapper."""
            return func(self, *args, **kwargs)

        GLib.idle_add(inner)

    return wrapper

