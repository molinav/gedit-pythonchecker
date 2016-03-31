"""main/controller.py

Store the plugin's main controller.
"""

import time
from gi.repository import Gedit
from gi.repository import GObject
from gi.repository import PeasGtk

from .. _decorators import threaded_with_glib
from .. _decorators import threaded_with_python
from .. conf.controller import Controller as ConfController
from .. conf.model import Configuration
from . model import CheckerPep8
from . model import CheckerPyLint
from . view import View
 

class Controller(GObject.Object, Gedit.WindowActivatable,
                 PeasGtk.Configurable):
    """Controller for the main plugin."""

    __gtype_name__ = "PythonChecker_Main_Controller"
    window = GObject.property(type=Gedit.Window)

    STATUSBAR_MESSAGE_DELAY = 3

    def __init__(self):
        """Run when creating a new instance of CheckerController."""

        GObject.threads_init()
        super(Controller, self).__init__()
        self.handlers = []
        self.errors = {}
        self.view = None

    def enable(self):
        """Add the plugin tab to the window panel."""

        # Create the treeview if it does not exist and check if the treeview
        # is already within a panel.
        if not self.view:
            self.view = View()
        if self.view.panel:
            self.disable()

        # Read panel location (True: side panel, False: bottom panel).
        db = Configuration()
        db_g = db.load("General")
        try:
            db_g["location"]
        except KeyError:
            db_g["location"] = True
        db.push()

        # Add tab to panel.
        if not db_g["location"]:
            panel = self.window.get_side_panel()
        else:
            panel = self.window.get_bottom_panel()
        self.view.add_to_panel(panel)

        # Create handlers.
        window = self.window
        call = window.connect("tab-added", self.on_tab_added)
        self.handlers.append((window, call))
        call = window.connect("tab-removed", self.update_panel)
        self.handlers.append((window, call))
        call = window.connect("active-tab-changed", self.update_panel)
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

        configurator_controller = ConfController()
        return configurator_controller.view

    def on_tab_added(self, window, tab, *args):
        """Trigger when a tab is added."""

        # Create document event connections.
        doc = tab.get_document()
        call = doc.connect("loaded", self.update_errors)
        self.handlers.append((doc, call))
        call = doc.connect("saved", self.update_errors)
        self.handlers.append((doc, call))

    @threaded_with_python
    def update_errors(self, *args):
        """Update the error list model based on the doc analysis."""

        # Get the document language and proceed only for Python files.
        doc = args[0]
        lang = doc.get_language()
        if lang and lang.get_name() in "Python 3":
            filepath = doc.get_uri_for_display()
            filename = doc.get_short_name_for_display()
            # Update statusbar message.
            msg = "Checking code in {}".format(filename)
            self.update_statusbar(msg, life=0)
            # Filter by activated checkers in the preferences values.
            db = Configuration()
            checkers = [CheckerPep8(), CheckerPyLint()]
            for c in checkers:
                db_c = db.load(c.NAME)
                try:
                    db_c["enable"]
                except KeyError:
                    db_c["enable"] = False
                if not db_c["enable"]:
                    checkers.remove(c)
            db = None
            # Call the checkers and store the output error instances.
            errors = (x for c in checkers for x in c.check_file(filepath))
            errors = sorted(errors, key=lambda x: (x.line, x.column))
            self.errors[filepath] = errors
            self.update_panel()
            # Update statusbar message.
            msg = "File {} successfully checked".format(filename)
            self.update_statusbar(msg)

    @threaded_with_glib
    def clear_statusbar(self):
        """Set the statusbar pristine."""

        try:
            statusbar = self.window.get_statusbar()
            context_id = statusbar.get_context_id(self.__gtype_name__)
            statusbar.remove_all(context_id)
        except AttributeError:
            pass

    @threaded_with_glib
    def push_to_statusbar(self, message):
        """Push a message to the statusbar."""

        try:
            statusbar = self.window.get_statusbar()
            context_id = statusbar.get_context_id(self.__gtype_name__)
            statusbar.push(context_id, message)
        except AttributeError:
            pass

    def update_statusbar(self, message, life=None):
        """Clean and push a message to the statusbar for a certain time."""

        life = life if life is not None else self.STATUSBAR_MESSAGE_DELAY

        self.clear_statusbar()
        self.push_to_statusbar(message)
        time.sleep(life)
        if life:
            self.clear_statusbar()

    def update_panel(self, *args):
        """Clean the panel and show errors from active document."""

        # Clean the panel error list.
        self.view.clear()
        # Locate the document within the tab if it exists.
        doc = self.window.get_active_document()
        if doc:
            # Get the filepath and update the panel error list.
            filepath = doc.get_uri_for_display()
            if filepath.startswith("/"):
                try:
                    for error in self.errors[filepath]:
                        self.view.append(error)
                except KeyError:
                    pass

