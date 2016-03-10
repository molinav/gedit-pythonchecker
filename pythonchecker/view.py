"""./view.py

This file stores the error list treeview with scrollbars.
"""

from io import StringIO
from subprocess import Popen
from subprocess import PIPE
from collections import namedtuple
from gi import require_version
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import GdkPixbuf

from . _decorators import threaded_with_glib
require_version("Gtk", "3.0")


class CheckerTreeView(Gtk.TreeView):
    """Generic class for an error treeview."""

    __gtype_name__ = "CheckerTreeView"

    _Column =\
        namedtuple("Column", ["name", "title", "renderer", "type"])
    _get_icon =\
        lambda icon: Gtk.IconTheme.load_icon(
            Gtk.IconTheme.get_default(), icon, 16, 0)

    COLUMNS = [
        _Column("Case", "",
                Gtk.CellRendererPixbuf, GdkPixbuf.Pixbuf),
        _Column("Code", "Code",
                Gtk.CellRendererText, GObject.TYPE_STRING),
        _Column("Line", "L",
                Gtk.CellRendererText, GObject.TYPE_INT),
        _Column("Column", "C",
                Gtk.CellRendererText, GObject.TYPE_INT),
        _Column("Message", "Message",
                Gtk.CellRendererText, GObject.TYPE_STRING)
    ]

    ERROR_ICONS = {
        "E": _get_icon("emblem-important"),
        "F": _get_icon("dialog-error"),
        "W": _get_icon("dialog-warning"),
        "C": _get_icon("dialog-information"),
        "R": _get_icon("dialog-question"),
    }

    def __init__(self):
        """Constructor of an error treeview."""

        super(CheckerTreeView, self).__init__()

        # Set treeview model.
        self.set_model(Gtk.ListStore(*[c.type for c in self.COLUMNS]))

        # Set treeview header.
        self.set_headers_visible(True)
        for i, c in enumerate(self.COLUMNS):
            column = Gtk.TreeViewColumn(c.title)
            cellrd = c.renderer()
            if c.type == GObject.TYPE_INT:
                cellrd.set_alignment(1, 0.5)
            column.pack_start(cellrd, False)
            attr = c.renderer.__name__.lstrip("CellRenderer").lower()
            column.add_attribute(cellrd, attr, i)
            column.set_resizable(True)
            column.set_reorderable(True)
            column.set_sort_column_id(i)
            self.append_column(column)

    @threaded_with_glib
    def append(self, error, icon):
        """Append an error row to the error list model."""

        try:
            self.props.model.append(
                (icon, error.code, error.line, error.column, error.message)
            )
        except AttributeError:
            pass

    @threaded_with_glib
    def clear(self):
        """Clear the error list model."""

        try:
            self.props.model.clear()
        except AttributeError:
            pass


class CheckerView(Gtk.ScrolledWindow):
    """Class for a plugin tab with scrollbars."""

    __gtype_name__ = "CheckerView"

    PANEL_NAME =\
        "Python Checker"
    PANEL_TITLE =\
        "Python Checker"
    PANEL_ICON =\
        Gtk.Image.new_from_stock(Gtk.STOCK_YES, Gtk.IconSize.MENU)
    VERSION_STR =\
        "gedit - Version "

    def __init__(self):
        """Create a new instance of CheckerView."""

        super(CheckerView, self).__init__()
        self.treeview = CheckerTreeView()
        self.add(self.treeview)
        self.panel = None
        self.version = self.get_gedit_version()

    def get_gedit_version(self):
        """Return Gedit version in hexadecimal format."""

        version = int("0x030000", 16)
        out = StringIO()
        try:
            call = Popen(["gedit", "--version"], stdout=PIPE, stderr=PIPE)
            out.write(call.communicate()[0].decode(encoding="UTF-8"))
            out.seek(0)
            lst = list(l.strip("\n") for l in out.readlines())
            lst = [l for l in lst if l.startswith(self.VERSION_STR)]
            if lst:
                lst = lst[-1].strip(self.VERSION_STR).split(" ")[0].split(".")
                lst = [int(x) for x in lst]
                version = int("0x{:02d}{:02d}{:02d}".format(*lst), 16)
        except BrokenPipeError:
            pass
        return version

    def add_to_panel(self, panel):
        """Add the plugin tab to the panel."""

        self.panel = panel
        if self.version < 0x031200:
            self.panel.add_item(
                self, self.PANEL_NAME, self.PANEL_TITLE,
                self.PANEL_ICON)
            self.panel.activate_item(self)
            self.treeview.show_all()
        else:
            self.show()
            self.panel.add_titled(self, self.PANEL_NAME, self.PANEL_TITLE)
            self.treeview.show_all()
            self.panel.set_visible_child(
                self.panel.get_child_by_name(self.PANEL_NAME))

    def remove_from_panel(self):
        """Remove the plugin tab from the panel."""

        if self.panel:
            if self.version < 0x031200:
                self.panel.remove_item(self)
            else:
                self.panel.remove(self)
            self.panel = None

    def append(self, error):
        """Append an error row to the error list model."""

        try:
            icon = self.treeview.ERROR_ICONS[error.case]
        except KeyError:
            icon = self.treeview.ERROR_ICONS["E"]

        self.treeview.append(error, icon)

    def clear(self):
        """Clear the error list model."""

        self.treeview.clear()


class CheckerConfiguratorPage(Gtk.Box):
    """Class defining pages within the preferences dialog."""

    __gtype_name__ = "CheckerConfiguratorPage"

    BORDER_WIDTH = 10
    UPDOWN = Gtk.Orientation.VERTICAL

    def __init__(self, name):
        """Create a new instance of CheckerConfiguratorPage."""

        super(CheckerConfiguratorPage, self).__init__(orientation=self.UPDOWN)
        self.set_border_width(self.BORDER_WIDTH)
        self.name = name

        # Set check button which enables or disables the checker.
        self.check_enable = Gtk.CheckButton("Enable {} checker".format(name))
        self.pack_start(self.check_enable, True, True, 0)


class CheckerConfiguratorView(Gtk.Notebook):
    """Class defining the content of the preferences dialog."""

    __gtype_name__ = "CheckerConfiguratorView"

    def __init__(self):
        """Create a new instance of CheckerConfiguratorView."""

        super(CheckerConfiguratorView, self).__init__()

        name1 = "Pep8"
        self.page1 = CheckerConfiguratorPage(name1)
        self.append_page(self.page1, Gtk.Label(name1))

        name2 = "PyLint"
        self.page2 = CheckerConfiguratorPage(name2)
        self.append_page(self.page2, Gtk.Label(name2))

