# modes.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""List the modes in the database.

The modes are ways of conducting the game, such as 'over the board' (OTB)
or 'online'.

"""
import tkinter

from solentware_bind.gui.bindings import Bindings

from . import modesgrid
from .eventspec import EventSpec
from ..core import identify_mode


class ModesError(Exception):
    """Raise exception in modes module."""


class Modes(Bindings):
    """Define widgets which list modes of games."""

    def __init__(self, master, database):
        """Create the modes widget."""
        super().__init__()
        self._modes_grid = modesgrid.ModesGrid(
            parent=master, database=database
        )

    @property
    def frame(self):
        """Return the top frame of the modes widget."""
        return self._modes_grid.frame

    @property
    def data_grid(self):
        """Return the modes widget."""
        return self._modes_grid

    def identify(self):
        """Identify bookmarked modes as selected mode."""
        title = EventSpec.menu_other_mode_identify[1]
        database = self.get_database(title)
        if not database:
            return
        modes_sel = self._modes_grid.selection
        modes_bmk = self._modes_grid.bookmarks
        if len(modes_sel) == 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="No mode is selected",
            )
            return False
        if len(modes_bmk) == 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="No modes are bookmarked so no changes done",
            )
            return False
        if modes_bmk == modes_sel:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="Selection and bookmark is same so no changes done",
            )
            return False
        new = set(modes_bmk)
        if new.intersection(modes_sel):
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="".join(
                    (
                        "Selection is one of bookmarked modes ",
                        "so no changes done",
                    )
                ),
            )
            return False
        message = identify_mode.identify(database, new, modes_sel)
        if message is not None:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message=message,
            )
            return False
        self.data_grid.bookmarks[:] = []  # When was clear() method added?

    def break_selected(self):
        """Undo identification of bookmarked modes as selection."""
        title = EventSpec.menu_other_mode_break[1]
        database = self.get_database(title)
        if not database:
            return
        modes_sel = self._modes_grid.selection
        modes_bmk = self._modes_grid.bookmarks
        if len(modes_sel) == 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="No mode is selected",
            )
            return False
        if len(modes_bmk) == 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="No modes are bookmarked so no changes done",
            )
            return False
        if modes_bmk == modes_sel:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="Selection and bookmark is same so no changes done",
            )
            return False
        new = set(modes_bmk)
        if new.intersection(modes_sel):
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="".join(
                    (
                        "Selection is one of bookmarked modes ",
                        "so no changes done",
                    )
                ),
            )
            return False
        message = identify_mode.break_bookmarked_aliases(
            database, new, modes_sel
        )
        if message is not None:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message=message,
            )
            return False
        self.data_grid.bookmarks[:] = []  # When was clear() method added?

    def split_all(self):
        """Undo identification of all aliases of selected mode."""
        title = EventSpec.menu_other_mode_split[1]
        database = self.get_database(title)
        if not database:
            return
        modes_sel = self._modes_grid.selection
        modes_bmk = self._modes_grid.bookmarks
        if len(modes_sel) == 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="No mode is selected",
            )
            return False
        if len(modes_bmk) != 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="Modes are bookmarked so no changes done",
            )
            return False
        message = identify_mode.split_aliases(database, modes_sel)
        if message is not None:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message=message,
            )
            return False

    def change_identity(self):
        """Undo identification of all aliases of selected mode."""
        title = EventSpec.menu_other_mode_change[1]
        database = self.get_database(title)
        if not database:
            return
        modes_sel = self._modes_grid.selection
        modes_bmk = self._modes_grid.bookmarks
        if len(modes_sel) == 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="No mode is selected",
            )
            return False
        if len(modes_bmk) != 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="Modes are bookmarked so no changes done",
            )
            return False
        message = identify_mode.change_aliases(database, modes_sel)
        if message is not None:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message=message,
            )
            return False

    def get_database(self, title):
        """Return database if modes list is attached to database.

        Return False otherwise after dialogue indicating problem.

        """
        modes_ds = self._modes_grid.datasource
        if modes_ds is None:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="".join(
                    (
                        "Modes list ",
                        "is not attached to database at present",
                    )
                ),
            )
            return False
        modes_db = modes_ds.dbhome
        if modes_db is None:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="".join(
                    (
                        "Modes list ",
                        "is not attached to database index at present",
                    )
                ),
            )
            return False
        return modes_db