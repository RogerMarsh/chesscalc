# persons.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""List the persons in the database."""

import tkinter

from solentware_bind.gui.bindings import Bindings

from . import personsgrid
from .eventspec import EventSpec
from ..core import identify_person


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
            return
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
            return
        elif len(persons_sel) == 0:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="No identified person is selected",
            )
            return
        elif len(persons_bmk) == 0:
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
            return
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
            return
        message = identify_person.break_person_into_picked_players(
            database, persons_sel, aliases
        )
        if message:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message=message,
            )
            return

    def split_all(self):
        """Undo identification of all player aliases as a person."""
        title = EventSpec.menu_player_split[1]
        database = self.get_database(title)
        if not database:
            return
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
        elif len(persons_sel) != 1:
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
        elif len(persons_bmk) != 0:
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
                return
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
            return
        message = identify_person.split_person_into_all_players(
            database, persons_sel
        )
        if message:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message=message,
            )
            return

    def change_identity(self):
        """Change identification of all player aliases as a person."""
        title = EventSpec.menu_player_change[1]
        database = self.get_database(title)
        if not database:
            return
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
        elif len(persons_sel) != 1:
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
        elif len(persons_bmk) != 0:
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
                return
        elif not tkinter.messagebox.askokcancel(
            parent=self.frame,
            title=title,
            message="".join(
                (
                        "The selected alias will become the identified ",
                        "person"
                )
            ),
        ):
            return
        message = identify_person.change_identified_person(
            database, persons_sel
        )
        if message:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message=message,
            )
            return

    def get_database(self, title):
        """Return database if identified players list is attached to database.

        Return False otherwise after dialogue indicating problem.

        """
        persons_ds = self._persons_grid.datasource
        if persons_ds is None:
            tkinter.messagebox.showinfo(
                parent=self._players,
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
                parent=self._players,
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
