# timecontrolsrow.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Create widgets that display header details of games from PGN files."""

import tkinter

from solentware_grid.gui import datarow

from ..core import performancerecord
from ..core import filespec
from ..core import constants


class TimeControlsRow(performancerecord.TimeControlDBrecord, datarow.DataRow):
    """Display a time control record detail in time control name order."""

    header_specification = [
        {
            datarow.WIDGET: tkinter.Label,
            datarow.WIDGET_CONFIGURE: dict(
                text=text, anchor=tkinter.CENTER
            ),
            datarow.GRID_CONFIGURE: dict(column=column, sticky=tkinter.EW),
            datarow.GRID_COLUMNCONFIGURE: dict(weight=0, uniform=uniform),
            datarow.ROW: 0,
        } for column, text, uniform in (
            (0, constants.TAG_TIMECONTROL, "u0"),
        )
    ]

    def __init__(self, database=None):
        """Extend, define layout of displayed time control data."""
        super().__init__()
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
            } for column, anchor in (
                (0, tkinter.CENTER),
            )
        ]

    def grid_row(self, **kargs):
        """Return tuple of instructions to create row.

        Create textitems argument for TimeControlsRow instance.

        """
        value = self.value
        return super().grid_row(
            textitems=(
                value.timecontrol if value.timecontrol is not None else "",
            ),
            **kargs
        )
