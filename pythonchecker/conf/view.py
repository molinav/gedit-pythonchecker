"""config/view.py

Store the plugin's preferences dialog.
"""

from gi import require_version
from gi.repository import Gtk

require_version("Gtk", "3.0")


class Page(Gtk.Box):
    """Page within the preferences dialog."""

    __gtype_name__ = "PythonChecker_Conf_Page"

    BORDER_WIDTH = 10

    VERTICAL = Gtk.Orientation.VERTICAL
    HORIZONTAL = Gtk.Orientation.HORIZONTAL

    def __init__(self, name):
        """Run when creating a new Page instance."""

        super(Page, self).__init__(orientation=self.VERTICAL)
        self.set_border_width(self.BORDER_WIDTH)
        self.name = name


class PageGeneral(Page):
    """Page oriented to general preferences."""

    __gtype_name__ = "PythonChecker_Conf_PageGeneral"

    def __init__(self, name):
        """Run when creating a new PageGeneral instance."""

        super(PageGeneral, self).__init__(name)

        # Set label and combobox to select plugin's location.
        label = Gtk.Label("Plugin location")
        combo_model = Gtk.ListStore(bool, str)
        combo_model.append([False, "Side panel"])
        combo_model.append([True, "Bottom panel"])
        renderer_text = Gtk.CellRendererText()
        self.combo_location = Gtk.ComboBox.new_with_model(combo_model)
        self.combo_location.pack_start(renderer_text, True)
        self.combo_location.add_attribute(renderer_text, "text", 1)

        # Add combobox and label to the configuration page.
        hbox = Gtk.Box(orientation=self.HORIZONTAL, spacing=0)
        hbox.pack_start(label, True, True, 0)
        hbox.pack_end(self.combo_location, True, True, 0)
        self.pack_start(hbox, True, True, 0)


class PageChecker(Page):
    """Page oriented to checker preferences."""

    __gtype_name__ = "PythonChecker_Conf_PageChecker"

    def __init__(self, name):
        """Run when creating a new PageChecker instance."""

        super(PageChecker, self).__init__(name)

        # Set check button which enables or disables the checker.
        label = "Enable {} checker".format(name)
        self.check_enable = Gtk.CheckButton(label)
        self.pack_start(self.check_enable, True, True, 0)


class View(Gtk.Notebook):
    """Page container for the preferences dialog."""

    __gtype_name__ = "PythonChecker_Conf_View"

    def __init__(self):
        """Run when creating a new View instance."""

        super(View, self).__init__()

        name0 = "General"
        self.page0 = PageGeneral(name0)
        self.append_page(self.page0, Gtk.Label(name0))

        name1 = "Pep8"
        self.page1 = PageChecker(name1)
        self.append_page(self.page1, Gtk.Label(name1))

        name2 = "PyLint"
        self.page2 = PageChecker(name2)
        self.append_page(self.page2, Gtk.Label(name2))

