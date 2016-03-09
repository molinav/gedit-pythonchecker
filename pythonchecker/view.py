"""./view.py

This file stores the error list treeview with scrollbars.
"""
 
from collections import namedtuple
from gi import require_version
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import GdkPixbuf
from io import StringIO
from subprocess import Popen
from subprocess import PIPE

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

        self.props.model.append(
            (icon, error.code, error.line, error.column, error.message)
        )

    @threaded_with_glib
    def clear(self):
        """Clear the error list model."""

        self.props.model.clear()


class CheckerView(Gtk.ScrolledWindow):
    """Class for a plugin tab with scrollbars."""

    __gtype_name__ = "CheckerView"

    PANEL_NAME =\
        "Python Checker"
    PANEL_TITLE =\
        "Python Checker"
    PANEL_ICON =\
        Gtk.Image.new_from_stock(Gtk.STOCK_YES, Gtk.IconSize.MENU)

    def __init__(self):
        """Create a new instance of CheckerView."""

        super(CheckerView, self).__init__()
        self.treeview = CheckerTreeView()
        self.add(self.treeview)
        self.panel = None
        self.version = self.get_gedit_version()

    def get_gedit_version(self):
        """Return Gedit version in hexadecimal format."""

        VERSION_STR = "gedit - Version "        
        version = int("0x030000", 16)
        out = StringIO()
        try:
            call = Popen(["gedit", "--version"], stdout=PIPE, stderr=PIPE)
            out.write(call.communicate()[0].decode(encoding="UTF-8"))
            out.seek(0)
            out = list(l.strip("\n") for l in out.readlines())
            out = [l for l in out if l.startswith(VERSION_STR)]
            if out:
                out = out[-1].strip(VERSION_STR).split(" ")[0].split(".")
                out = [int(x) for x in out]
                version = int("0x{:02d}{:02d}{:02d}".format(*out), 16)
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

