# timecontrols.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""List the time controls in the database."""

import tkinter

from solentware_bind.gui.bindings import Bindings

from . import timecontrolsgrid
from .eventspec import EventSpec
from ..core import identify_timecontrol


class TimeControlsError(Exception):
    """Raise exception in timecontrols module."""


class TimeControls(Bindings):
    """Define widgets which list time controls of games."""

    def __init__(self, master, database):
        """Create the time controls widget."""
        super().__init__()
        self._time_limits_grid = timecontrolsgrid.TimeControlsGrid(
            parent=master, database=database
        )

    @property
    def frame(self):
        """Return the top frame of the time controls widget."""
        return self._time_limits_grid.frame

    @property
    def data_grid(self):
        """Return the time controls widget."""
        return self._time_limits_grid

    def identify(self):
        """Identify bookmarked time controls as selected time control."""
        title = EventSpec.menu_other_time_identify[1]
        database = self.get_database(title)
        if not database:
            return
        limits_sel = self._time_limits_grid.selection
        limits_bmk = self._time_limits_grid.bookmarks
        if len(limits_sel) == 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="No time control is selected",
            )
            return False
        if len(limits_bmk) == 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="No time controls are bookmarked so no changes done",
            )
            return False
        if limits_bmk == limits_sel:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="Selection and bookmark is same so no changes done",
            )
            return False
        new = set(limits_bmk)
        if new.intersection(limits_sel):
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="".join(
                    (
                        "Selection is one of bookmarked time controls ",
                        "so no changes done",
                    )
                ),
            )
            return False
        message = identify_timecontrol.identify(database, new, limits_sel)
        if message is not None:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message=message,
            )
            return False
        self.data_grid.bookmarks[:] = []  # When was clear() method added?

    def break_selected(self):
        """Undo identification of bookmarked time controls as selection."""
        title = EventSpec.menu_other_time_break[1]
        database = self.get_database(title)
        if not database:
            return
        limits_sel = self._time_limits_grid.selection
        limits_bmk = self._time_limits_grid.bookmarks
        if len(limits_sel) == 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="No time control is selected",
            )
            return False
        if len(limits_bmk) == 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="No time controls are bookmarked so no changes done",
            )
            return False
        if limits_bmk == limits_sel:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="Selection and bookmark is same so no changes done",
            )
            return False
        new = set(limits_bmk)
        if new.intersection(limits_sel):
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="".join(
                    (
                        "Selection is one of bookmarked time controls ",
                        "so no changes done",
                    )
                ),
            )
            return False
        message = identify_timecontrol.break_bookmarked_aliases(
            database, new, limits_sel
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
        """Undo identification of all aliases of selected time control."""
        title = EventSpec.menu_other_time_split[1]
        database = self.get_database(title)
        if not database:
            return
        limits_sel = self._time_limits_grid.selection
        limits_bmk = self._time_limits_grid.bookmarks
        if len(limits_sel) == 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="No time control is selected",
            )
            return False
        if len(limits_bmk) != 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="Time controls are bookmarked so no changes done",
            )
            return False
        message = identify_timecontrol.split_aliases(database, limits_sel)
        if message is not None:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message=message,
            )
            return False

    def change_identity(self):
        """Undo identification of all aliases of selected time control."""
        title = EventSpec.menu_other_time_change[1]
        database = self.get_database(title)
        if not database:
            return
        limits_sel = self._time_limits_grid.selection
        limits_bmk = self._time_limits_grid.bookmarks
        if len(limits_sel) == 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="No time control is selected",
            )
            return False
        if len(limits_bmk) != 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="Time controls are bookmarked so no changes done",
            )
            return False
        message = identify_timecontrol.change_aliases(database, limits_sel)
        if message is not None:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message=message,
            )
            return False

    def get_database(self, title):
        """Return database if time controls list is attached to database.

        Return False otherwise after dialogue indicating problem.

        """
        limits_ds = self._time_limits_grid.datasource
        if limits_ds is None:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="".join(
                    (
                        "Time controls list ",
                        "is not attached to database at present",
                    )
                ),
            )
            return False
        limits_db = limits_ds.dbhome
        if limits_db is None:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="".join(
                    (
                        "Time controls list ",
                        "is not attached to database index at present",
                    )
                ),
            )
            return False
        return limits_db
