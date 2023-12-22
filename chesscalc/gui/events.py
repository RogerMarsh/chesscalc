# events.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""List the events in the database."""

import tkinter

from solentware_bind.gui.bindings import Bindings

from . import eventsgrid
from .eventspec import EventSpec
from ..core import identify_event


class EventsError(Exception):
    """Raise exception in events module."""


class Events(Bindings):
    """Define widgets which list events of games."""

    def __init__(self, master, database):
        """Create the events widget."""
        super().__init__()
        self._events_grid = eventsgrid.EventsGrid(
            parent=master, database=database
        )

    @property
    def frame(self):
        """Return the top frame of the events widget."""
        return self._events_grid.frame

    @property
    def data_grid(self):
        """Return the events widget."""
        return self._events_grid

    def identify(self):
        """Identify bookmarked events as selected event."""
        title = EventSpec.menu_other_event_identify[1]
        database = self.get_database(title)
        if not database:
            return
        events_sel = self._events_grid.selection
        events_bmk = self._events_grid.bookmarks
        if len(events_sel) == 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="No event is selected",
            )
            return False
        if len(events_bmk) == 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="No events are bookmarked so no changes done",
            )
            return False
        if events_bmk == events_sel:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="Selection and bookmark is same so no changes done",
            )
            return False
        new = set(events_bmk)
        if new.intersection(events_sel):
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="".join(
                    (
                        "Selection is one of bookmarked events ",
                        "so no changes done",
                    )
                ),
            )
            return False
        message = identify_event.identify(database, new, events_sel)
        if message is not None:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message=message,
            )
            return False
        self.data_grid.bookmarks[:] = []  # When was clear() method added?

    def break_selected(self):
        """Undo identification of bookmarked events as selection event."""
        title = EventSpec.menu_other_event_break[1]
        database = self.get_database(title)
        if not database:
            return
        events_sel = self._events_grid.selection
        events_bmk = self._events_grid.bookmarks
        if len(events_sel) == 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="No event is selected",
            )
            return False
        if len(events_bmk) == 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="No events are bookmarked so no changes done",
            )
            return False
        if events_bmk == events_sel:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="Selection and bookmark is same so no changes done",
            )
            return False
        new = set(events_bmk)
        if new.intersection(events_sel):
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="".join(
                    (
                        "Selection is one of bookmarked events ",
                        "so no changes done",
                    )
                ),
            )
            return False
        message = identify_event.break_bookmarked_aliases(
            database, new, events_sel
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
        """Undo identification of all aliases of selected event."""
        title = EventSpec.menu_other_event_split[1]
        database = self.get_database(title)
        if not database:
            return
        events_sel = self._events_grid.selection
        events_bmk = self._events_grid.bookmarks
        if len(events_sel) == 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="No event is selected",
            )
            return False
        if len(events_bmk) != 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="Events are bookmarked so no changes done",
            )
            return False
        message = identify_event.split_aliases(database, events_sel)
        if message is not None:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message=message,
            )
            return False

    def change_identity(self):
        """Undo identification of all aliases of selected event."""
        title = EventSpec.menu_other_event_change[1]
        database = self.get_database(title)
        if not database:
            return
        events_sel = self._events_grid.selection
        events_bmk = self._events_grid.bookmarks
        if len(events_sel) == 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="No event is selected",
            )
            return False
        if len(events_bmk) != 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="Events are bookmarked so no changes done",
            )
            return False
        message = identify_event.change_aliases(database, events_sel)
        if message is not None:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message=message,
            )
            return False

    def get_database(self, title):
        """Return database if events list is attached to database.

        Return False otherwise after dialogue indicating problem.

        """
        events_ds = self._events_grid.datasource
        if events_ds is None:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="".join(
                    (
                        "Events list ",
                        "is not attached to database at present",
                    )
                ),
            )
            return False
        events_db = events_ds.dbhome
        if events_db is None:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="".join(
                    (
                        "Events list ",
                        "is not attached to database index at present",
                    )
                ),
            )
            return False
        return events_db
