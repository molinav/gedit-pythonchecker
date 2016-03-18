"""config/view.py

Store the plugin's preferences dialog.
"""

from gi import require_version
from gi.repository import Gtk
require_version("Gtk", "3.0")


class CheckerConfiguratorPage(Gtk.Box):
    """Class defining pages within the preferences dialog."""

    __gtype_name__ = "CheckerConfiguratorPage"

    BORDER_WIDTH = 10

    def __init__(self, name):
        """Create a new instance of CheckerConfiguratorPage."""

        super(CheckerConfiguratorPage, self).__init__(
            orientation=Gtk.Orientation.VERTICAL)
        self.set_border_width(self.BORDER_WIDTH)
        self.name = name


class CheckerConfiguratorPageGeneral(CheckerConfiguratorPage):
    """Class defining page for general preferences."""

    def __init__(self, name):

        super(CheckerConfiguratorPageGeneral, self).__init__(name)

        # Set combobox to select plugin's location.
        label = Gtk.Label("Plugin location ")
        self.combo_model = Gtk.ListStore(bool, str)
        self.combo_model.append([False, "Side panel"])
        self.combo_model.append([True, "Bottom panel"])
        self.combo_location = Gtk.ComboBox.new_with_model(self.combo_model)
        renderer_text = Gtk.CellRendererText()
        self.combo_location.pack_start(renderer_text, True)
        self.combo_location.add_attribute(renderer_text, "text", 1)

        # Add combobox and label to the configuration page.
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        hbox.pack_start(label, True, True, 0)
        hbox.pack_end(self.combo_location, True, True, 0)
        self.pack_start(hbox, True, True, 0)


class CheckerConfiguratorPageChecker(CheckerConfiguratorPage):
    """Class defining page for checker preferences."""

    def __init__(self, name):

        super(CheckerConfiguratorPageChecker, self).__init__(name)

        # Set check button which enables or disables the checker.
        self.check_enable = Gtk.CheckButton("Enable {} checker".format(name))
        self.pack_start(self.check_enable, True, True, 0)


class CheckerConfiguratorView(Gtk.Notebook):
    """Class defining the content of the preferences dialog."""

    __gtype_name__ = "CheckerConfiguratorView"

    def __init__(self):
        """Create a new instance of CheckerConfiguratorView."""

        super(CheckerConfiguratorView, self).__init__()

        name0 = "General"
        self.page0 = CheckerConfiguratorPageGeneral(name0)
        self.append_page(self.page0, Gtk.Label(name0))

        name1 = "Pep8"
        self.page1 = CheckerConfiguratorPageChecker(name1)
        self.append_page(self.page1, Gtk.Label(name1))

        name2 = "PyLint"
        self.page2 = CheckerConfiguratorPageChecker(name2)
        self.append_page(self.page2, Gtk.Label(name2))

