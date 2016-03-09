from threading import Thread
from gi.repository import GLib


def threaded_with_python(func):

    def wrapper(self, *args, **kwargs):

        def inner():
            
            return func(self, *args, **kwargs)

        thread = Thread(target=inner)
        thread.daemon = True
        thread.start()

    return wrapper


def threaded_with_glib(func):

    def wrapper(self, *args, **kwargs):

        def inner():
            return func(self, *args, **kwargs)

        GLib.idle_add(inner)

    return wrapper

