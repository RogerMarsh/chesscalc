# selectorsrow.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Create widgets that display header details of game selection rules."""

import tkinter

from solentware_grid.gui import datarow

from ..core import performancerecord
from ..core import filespec
from ..core import constants


class SelectorsRow(performancerecord.SelectorDBrecord, datarow.DataRow):
    """Display a Game Selector record."""

    header_specification = [
        {
            datarow.WIDGET: tkinter.Label,
            datarow.WIDGET_CONFIGURE: dict(text=text, anchor=tkinter.CENTER),
            datarow.GRID_CONFIGURE: dict(column=column, sticky=tkinter.EW),
            datarow.GRID_COLUMNCONFIGURE: dict(weight=0, uniform=uniform),
            datarow.ROW: 0,
        }
        for column, text, uniform in (
            (0, "Rule", "u0"),
            (1, "From", "u1"),
            (2, "To", "u2"),
            (3, "Person", "u3"),
            (4, "Events", "u4"),
        )
    ]

    def __init__(self, database=None):
        """Extend, define the data displayed from the Game Selector record."""
        super().__init__(valueclass=performancerecord.SelectorDBvalue)
        self.set_database(database)
        GRID_CONFIGURE = datarow.GRID_CONFIGURE
        WIDGET_CONFIGURE = datarow.WIDGET_CONFIGURE
        WIDGET = datarow.WIDGET
        ROW = datarow.ROW
        self.row_specification = [
            {
                WIDGET: tkinter.Label,
                WIDGET_CONFIGURE: dict(anchor=anchor),
                GRID_CONFIGURE: dict(column=column, sticky=tkinter.EW),
                ROW: 0,
            }
            for column, anchor in (
                (0, tkinter.CENTER),
                (1, tkinter.CENTER),
                (2, tkinter.CENTER),
                (3, tkinter.CENTER),
                (4, tkinter.CENTER),
            )
        ]

    def grid_row(self, **kargs):
        """Return tuple of instructions to create row.

        Create textitems argument for PersonsRow instance.

        """
        value = self.value
        return super().grid_row(
            textitems=(
                value.name if value.name is not None else "",
                value.from_date if value.from_date is not None else "",
                value.to_date if value.to_date is not None else "",
                value.person_identity
                if value.person_identity is not None
                else "",
                value.event_names if value.event_names is not None else "",
            ),
            **kargs
        )
