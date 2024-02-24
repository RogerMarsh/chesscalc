# persons.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""List the persons in the database."""

import tkinter
import os

from solentware_bind.gui.bindings import Bindings

from . import personsgrid
from .eventspec import EventSpec
from ..core import identify_person
from ..core import export
from ..core import configuration
from ..core import constants


class PersonsError(Exception):
    """Raise exception in persons module."""


class Persons(Bindings):
    """Define widgets which list persons not identified as a person."""

    def __init__(self, master, database):
        """Create the persons widget."""
        super().__init__()
        self._persons_grid = personsgrid.PersonsGrid(
            parent=master, database=database
        )

    @property
    def frame(self):
        """Return the persons widget."""
        return self._persons_grid.frame

    @property
    def data_grid(self):
        """Return the persons widget."""
        return self._persons_grid

    def break_selected(self):
        """Undo identification of selected players as a person."""
        title = EventSpec.menu_player_break[1]
        database = self.get_database(title)
        if not database:
            return None
        persons_sel = self._persons_grid.selection
        persons_bmk = self._persons_grid.bookmarks
        if len(persons_sel) == 0 and len(persons_bmk) == 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="".join(
                    (
                        "No identified person is selected and no aliases ",
                        "are bookmarked to be made new players",
                    )
                ),
            )
            return False
        if len(persons_sel) == 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="No identified person is selected",
            )
            return False
        if len(persons_bmk) == 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="".join(
                    (
                        "No aliases ",
                        "are bookmarked to be made new players",
                    )
                ),
            )
            return False
        aliases = set(persons_bmk)
        if persons_sel[0] in aliases:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="".join(
                    (
                        "Cannot break associations when selected entry ",
                        "is also bookmarked",
                    )
                ),
            )
            return False
        message = identify_person.break_person_into_picked_players(
            database, persons_sel, aliases
        )
        if message:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message=message,
            )
            return False
        return True

    def split_all(self):
        """Undo identification of all player aliases as a person."""
        title = EventSpec.menu_player_split[1]
        database = self.get_database(title)
        if not database:
            return None
        persons_sel = self._persons_grid.selection
        persons_bmk = self._persons_grid.bookmarks
        if len(persons_sel) == 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="".join(
                    (
                        "No identified person is selected to split ",
                        "into all aliases",
                    )
                ),
            )
            return False
        if len(persons_sel) != 1:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="".join(
                    (
                        "Exactly one identified person must be selected ",
                        "to split into all aliases",
                    )
                ),
            )
            return False
        if len(persons_bmk) != 0:
            if not tkinter.messagebox.askokcancel(
                parent=self.frame,
                title=title,
                message="".join(
                    (
                        "The selected identified person will split into all "
                        "aliases (bookmarks on identified persons are "
                        "ignored)",
                    )
                ),
            ):
                return False
        elif not tkinter.messagebox.askokcancel(
            parent=self.frame,
            title=title,
            message="".join(
                (
                    "The selected identified person will split into all "
                    "aliases",
                )
            ),
        ):
            return False
        message = identify_person.split_person_into_all_players(
            database, persons_sel
        )
        if message:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message=message,
            )
            return False
        return True

    def change_identity(self):
        """Change identification of all player aliases as a person."""
        title = EventSpec.menu_player_change[1]
        database = self.get_database(title)
        if not database:
            return None
        persons_sel = self._persons_grid.selection
        persons_bmk = self._persons_grid.bookmarks
        if len(persons_sel) == 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="".join(
                    (
                        "No identified person is selected to have ",
                        "identity changed",
                    )
                ),
            )
            return False
        if len(persons_sel) != 1:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="".join(
                    (
                        "Exactly one identified person must be selected ",
                        "to change identity",
                    )
                ),
            )
            return False
        if len(persons_bmk) != 0:
            if not tkinter.messagebox.askokcancel(
                parent=self.frame,
                title=title,
                message="".join(
                    (
                        "The selected alias will become the identified ",
                        "person (bookmarks on identified persons are "
                        "ignored)",
                    )
                ),
            ):
                return False
        elif not tkinter.messagebox.askokcancel(
            parent=self.frame,
            title=title,
            message="".join(
                ("The selected alias will become the identified ", "person")
            ),
        ):
            return False
        message = identify_person.change_identified_person(
            database, persons_sel
        )
        if message:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message=message,
            )
            return False
        return True

    def export_selected_players(self):
        """Export players for selection and bookmarked events."""
        title = EventSpec.menu_player_export[1]
        database = self.get_database(title)
        if not database:
            return None
        persons_sel = self._persons_grid.selection
        persons_bmk = self._persons_grid.bookmarks
        if len(persons_sel) + len(persons_bmk) == 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="No identified persons are selected or bookmarked",
            )
            return False
        exporter = export.ExportPersons(database, persons_bmk, persons_sel)
        exporter.prepare_export_data()
        status = exporter.prepare_export_data()
        if status.error_message is not None:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                message="\n\n".join(
                    (
                        "Export of selected persons failed",
                        status.error_message,
                    )
                ),
                title=title,
            )
            return False
        serialized_data = exporter.export_repr()
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
                message="Export of persons cancelled",
                title=title,
            )
            return False
        conf.set_configuration_value(
            constants.RECENT_EXPORT_DIRECTORY,
            conf.convert_home_directory_to_tilde(os.path.dirname(export_file)),
        )
        # gives time for destruction of dialogue and widget refresh
        # does nothing for obscuring and revealing application later
        self.frame.after_idle(
            self.try_command(export.write_export_file, self.frame),
            export_file,
            serialized_data,
        )
        return True

    def get_database(self, title):
        """Return database if identified players list is attached to database.

        Return False otherwise after dialogue indicating problem.

        """
        persons_ds = self._persons_grid.datasource
        if persons_ds is None:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="".join(
                    (
                        "Identified Players list ",
                        "is not attached to database at present",
                    )
                ),
            )
            return False
        persons_db = persons_ds.dbhome
        if persons_db is None:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="".join(
                    (
                        "Identified Players list ",
                        "is not attached to database index at present",
                    )
                ),
            )
            return False
        return persons_db
