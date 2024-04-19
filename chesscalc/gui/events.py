# events.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""List the events in the database."""

import tkinter
import os
from multiprocessing import dummy

from solentware_bind.gui.bindings import Bindings

from . import eventsgrid
from .eventspec import EventSpec
from ..core import identify_event
from ..core import export
from ..core import configuration
from ..core import constants


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

    def identify(self, update_widget_and_join_loop):
        """Identify bookmarked events as selected event."""
        title = EventSpec.menu_other_event_identify[1]
        database = self.get_database(title)
        if not database:
            return None
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
        answer = {"message": None}
        thread = dummy.DummyProcess(
            target=identify_event.identify,
            args=(database, new, events_sel, answer),
        )
        thread.start()
        update_widget_and_join_loop(thread)
        if answer["message"]:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message=answer["message"],
            )
            return False
        return True

    def break_selected(self, update_widget_and_join_loop):
        """Undo identification of bookmarked events as selection event."""
        title = EventSpec.menu_other_event_break[1]
        database = self.get_database(title)
        if not database:
            return None
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
        answer = {"message": None}
        thread = dummy.DummyProcess(
            target=identify_event.break_bookmarked_aliases,
            args=(database, new, events_sel, answer),
        )
        thread.start()
        update_widget_and_join_loop(thread)
        if answer["message"]:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message=answer["message"],
            )
            return False
        return True

    def split_all(self, update_widget_and_join_loop):
        """Undo identification of all aliases of selected event."""
        title = EventSpec.menu_other_event_split[1]
        database = self.get_database(title)
        if not database:
            return None
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
        answer = {"message": None}
        thread = dummy.DummyProcess(
            target=identify_event.split_aliases,
            args=(database, events_sel, answer),
        )
        thread.start()
        update_widget_and_join_loop(thread)
        if answer["message"]:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message=answer["message"],
            )
            return False
        return True

    def change_identity(self, update_widget_and_join_loop):
        """Undo identification of all aliases of selected event."""
        title = EventSpec.menu_other_event_change[1]
        database = self.get_database(title)
        if not database:
            return None
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
        answer = {"message": None}
        thread = dummy.DummyProcess(
            target=identify_event.change_aliases,
            args=(database, events_sel, answer),
        )
        thread.start()
        update_widget_and_join_loop(thread)
        if answer["message"]:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message=answer["message"],
            )
            return False
        return True

    def _export_players_in_selected_events(
        self, database, events_bmk, events_sel, answer
    ):
        """Prepare player data for export."""
        exporter = export.ExportEventPersons(database, events_bmk, events_sel)
        answer["status"] = exporter.prepare_export_data()
        if answer["status"].error_message is None:
            answer["serialized_data"] = exporter.export_repr()

    def export_players_in_selected_events(self, update_widget_and_join_loop):
        """Export players for selection and bookmarked events."""
        title = EventSpec.menu_other_event_export_persons[1]
        database = self.get_database(title)
        if not database:
            return None
        events_sel = self._events_grid.selection
        events_bmk = self._events_grid.bookmarks
        if len(events_sel) + len(events_bmk) == 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="No events are selected or bookmarked",
            )
            return False
        answer = {"status": None, "serialized_data": None}
        thread = dummy.DummyProcess(
            target=self._export_players_in_selected_events,
            args=(database, events_bmk, events_sel, answer),
        )
        thread.start()
        update_widget_and_join_loop(thread)
        if answer["status"] is None:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                message="\n\n".join(
                    (
                        "Export of event persons failed",
                        "Unable to extract data",
                    )
                ),
                title=title,
            )
            return False
        if answer["status"].error_message is not None:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                message="\n\n".join(
                    (
                        "Export of event persons failed",
                        answer["status"].error_message,
                    )
                ),
                title=title,
            )
            return False
        conf = configuration.Configuration()
        initdir = conf.get_configuration_value(
            constants.RECENT_EXPORT_DIRECTORY
        )
        export_file = tkinter.filedialog.asksaveasfilename(
            parent=self.frame,
            title=title,
            initialdir=initdir,
            initialfile="export-identities.txt",
        )
        if not export_file:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                message="Export of event persons cancelled",
                title=title,
            )
            return False
        conf.set_configuration_value(
            constants.RECENT_EXPORT_DIRECTORY,
            conf.convert_home_directory_to_tilde(os.path.dirname(export_file)),
        )
        thread = dummy.DummyProcess(
            target=export.write_export_file,
            args=(export_file, answer["serialized_data"]),
        )
        thread.start()
        update_widget_and_join_loop(thread)
        return True

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
