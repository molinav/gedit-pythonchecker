"""./controller.py

This file stores the plugin controller class.
"""

import time
from gi.repository import GObject
from gi.repository import Gedit
from gi.repository import PeasGtk

from . _decorators import threaded_with_glib
from . _decorators import threaded_with_python
from . model import CheckerPep8
from . model import CheckerPyLint
from . model import CheckerConfigurator
from . view import CheckerView
from . view import CheckerConfiguratorView


class CheckerController(GObject.Object, Gedit.WindowActivatable,
                        PeasGtk.Configurable):
    """Controller for the main plugin."""

    __gtype_name__ = "CheckerController"
    window = GObject.property(type=Gedit.Window)

    STATUSBAR_MESSAGE_DELAY = 3

    def __init__(self):
        """Create a new instance of CheckerController."""

        GObject.threads_init()
        super(CheckerController, self).__init__()
        self.handlers = []
        self.view = None

    def enable(self):
        """Add the plugin tab to the window panel."""

        if not self.view:

            # Add tab to panel.
            panel = self.window.get_side_panel()
            self.view = CheckerView()
            self.view.add_to_panel(panel)

            # Create handlers.
            window = self.window
            call = window.connect("tab-added", self.on_tab_added)
            self.handlers.append((window, call))
            call = window.connect("tab-removed", self.on_tab_removed)
            self.handlers.append((window, call))
            call = window.connect("active-tab-changed", self.on_tab_changed)
            self.handlers.append((window, call))

    def disable(self):
        """Remove the plugin tab from the window panel."""

        if self.view:

            # Remove tab from panel.
            self.view.remove_from_panel()

            # Remove handlers.
            for obj, handler in self.handlers:
                obj.disconnect(handler)

    def configure(self):
        """Load a dialog to set plugin preferences."""

        configurator_controller = CheckerConfiguratorController()
        return configurator_controller.view

    def on_doc_loaded(self, *args):
        """Handler triggered when a document is loaded."""

        self.update(*args)

    def on_doc_saved(self, *args):
        """Handler triggered when a document is saved."""

        self.update(*args)

    def on_tab_added(self, *args):
        """Handler triggered when a tab is added."""

        tab = args[1]
        # Create document event connections.
        doc = tab.get_document()
        call = doc.connect("loaded", self.on_doc_loaded)
        self.handlers.append((doc, call))
        call = doc.connect("saved", self.on_doc_saved)
        self.handlers.append((doc, call))

    def on_tab_removed(self, *args):
        """Handler triggered when a tab is removed."""

        window = args[0]
        # Clear the side panel in case there are no tabs opened.
        active_tab = window.get_active_tab()
        if not active_tab:
            self.view.clear()

    def on_tab_changed(self, *args):
        """Handler triggered when the active tab is changed."""

        self.update(*args)

    @threaded_with_python
    def update(self, *args):
        """Update the error list model based on the doc changes."""

        self.view.clear()
        active_view = self.window.get_active_view()

        if active_view:

            lang = self.window.get_active_document().get_language()

            if lang and lang.get_name() in "Python 3":

                active_buffer = active_view.get_buffer()
                filepath = active_buffer.get_uri_for_display()
                filename = active_buffer.get_short_name_for_display()

                msg = "Checking code in {}".format(filename)
                self.update_statusbar(msg, life=0)

                db = CheckerConfigurator()
                checkers = [CheckerPep8(), CheckerPyLint()]
                checkers = [c for c in checkers if db.load(c.NAME)["enable"]]
                db = None

                errors = (x for c in checkers for x in c.check_file(filepath))
                errors = sorted(errors, key=lambda x: (x.line, x.column))

                active_view = self.window.get_active_view()
                if active_view:
                    active_buffer = active_view.get_buffer()
                    filepath2 = active_buffer.get_uri_for_display()
                    if filepath == filepath2:
                        self.view.clear()
                        for error in errors:
                            self.view.append(error)
                        msg = "File {} successfully checked".format(filename)
                        self.update_statusbar(msg)

    @threaded_with_glib
    def clear_statusbar(self):
        """Set the statusbar pristine."""

        statusbar = self.window.get_statusbar()
        context_id = statusbar.get_context_id(self.__gtype_name__)

        statusbar.remove_all(context_id)

    @threaded_with_glib
    def push_to_statusbar(self, message):
        """Push a message to the statusbar."""

        statusbar = self.window.get_statusbar()
        context_id = statusbar.get_context_id(self.__gtype_name__)

        statusbar.push(context_id, message)

    def update_statusbar(self, message, life=None):
        """Clean and push a message to the statusbar for a certain time."""

        life = life if life is not None else self.STATUSBAR_MESSAGE_DELAY

        self.clear_statusbar()
        self.push_to_statusbar(message)
        time.sleep(life)
        if life:
            self.clear_statusbar()

    def _get_active_text(self):
        """Return the text from the active document."""

        active_view = self.window.get_active_view()

        if active_view:

            active_doc = self.window.get_active_document()

            begin = active_doc.get_start_iter()
            end = active_doc.get_end_iter()

            return active_view.get_buffer().get_text(begin, end, False)


class CheckerConfiguratorController(object):
    """Controller for the preferences dialog."""

    def __init__(self):
        """Return a new instance of CheckerConfiguratorController."""

        # Load options from json file and preferences dialog.
        self.database = CheckerConfigurator()
        self.view = CheckerConfiguratorView()

        for page in self.view.get_children():

            # Get property "enable".
            args = self.database.load(page.name)
            try:
                args["enable"]
            except KeyError:
                args["enable"] = False
            page.check_enable.set_active(args["enable"])
            page.check_enable.connect("toggled", self.on_check_enable_toggled)

        # Create handlers.
        self.view.connect("destroy", self.on_closed)

    def on_closed(self, *args):
        """Handler triggered when the preferences dialog is closed."""

        self.database.push()

    def on_check_enable_toggled(self, check_enable):
        """Handler triggered when the enable check is toggled."""

        page = check_enable.get_parent()
        args = self.database.load(page.name)
        args["enable"] = not args["enable"]

