# gamesrow.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Create widgets that display header details of games from PGN files."""

import tkinter

from solentware_grid.gui import datarow

from ..core import performancerecord
from ..core import constants


class GamesRow(performancerecord.GameDBrecord, datarow.DataRow):
    """Display a Game record."""

    header_specification = [
        {
            datarow.WIDGET: tkinter.Label,
            datarow.WIDGET_CONFIGURE: dict(text=text, anchor=tkinter.CENTER),
            datarow.GRID_CONFIGURE: dict(column=column, sticky=tkinter.EW),
            datarow.GRID_COLUMNCONFIGURE: dict(weight=0, uniform=uniform),
            datarow.ROW: 0,
        }
        for column, text, uniform in (
            (0, constants.TAG_EVENT, "u0"),
            (1, constants.TAG_EVENTDATE, "u1"),
            (2, constants.TAG_SECTION, "u2"),
            (3, constants.TAG_STAGE, "u3"),
            (4, constants.TAG_DATE, "u4"),
            (5, constants.TAG_WHITE, "u5"),
            (6, constants.TAG_WHITEFIDEID, "u6"),
            (7, constants.TAG_WHITETEAM, "u7"),
            (8, constants.TAG_RESULT, "u8"),
            (9, constants.TAG_BLACK, "u9"),
            (10, constants.TAG_BLACKFIDEID, "ua"),
            (11, constants.TAG_BLACKTEAM, "ub"),
            (12, constants.TAG_SITE, "uc"),
            (13, constants.TAG_ROUND, "ud"),
            (14, constants.TAG_BOARD, "ue"),
            (15, constants.TAG_WHITEELO, "uf"),
            (16, constants.TAG_BLACKELO, "ug"),
            (17, constants.FILE, "uh"),
            (18, constants.GAME, "ui"),
        )
    ]

    def __init__(self, database=None):
        """Extend, define the data displayed from the Game record."""
        super().__init__()
        self.set_database(database)
        self.row_specification = [
            {
                datarow.WIDGET: tkinter.Label,
                datarow.WIDGET_CONFIGURE: dict(anchor=anchor),
                datarow.GRID_CONFIGURE: dict(column=column, sticky=tkinter.EW),
                datarow.ROW: 0,
            }
            for column, anchor in (
                (0, tkinter.CENTER),
                (1, tkinter.CENTER),
                (2, tkinter.CENTER),
                (3, tkinter.CENTER),
                (4, tkinter.CENTER),
                (5, tkinter.CENTER),
                (6, tkinter.CENTER),
                (7, tkinter.CENTER),
                (8, tkinter.CENTER),
                (9, tkinter.CENTER),
                (10, tkinter.CENTER),
                (11, tkinter.CENTER),
                (12, tkinter.CENTER),
                (13, tkinter.CENTER),
                (14, tkinter.CENTER),
                (15, tkinter.CENTER),
                (16, tkinter.CENTER),
                (17, tkinter.CENTER),
                (18, tkinter.CENTER),
            )
        ]

    def grid_row(self, **kargs):
        """Return tuple of instructions to create row.

        Create textitems argument for GamesRow instance.

        """
        pgn_headers = self.value.headers
        reference = self.value.reference
        return super().grid_row(
            textitems=(
                pgn_headers.get(constants.TAG_EVENT, ""),
                pgn_headers.get(constants.TAG_EVENTDATE, ""),
                pgn_headers.get(constants.TAG_SECTION, ""),
                pgn_headers.get(constants.TAG_STAGE, ""),
                pgn_headers.get(constants.TAG_DATE, ""),
                pgn_headers.get(constants.TAG_WHITE, ""),
                pgn_headers.get(constants.TAG_WHITEFIDEID, ""),
                pgn_headers.get(constants.TAG_WHITETEAM, ""),
                pgn_headers.get(constants.TAG_RESULT, ""),
                pgn_headers.get(constants.TAG_BLACK, ""),
                pgn_headers.get(constants.TAG_BLACKFIDEID, ""),
                pgn_headers.get(constants.TAG_BLACKTEAM, ""),
                pgn_headers.get(constants.TAG_SITE, ""),
                pgn_headers.get(constants.TAG_ROUND, ""),
                pgn_headers.get(constants.TAG_BOARD, ""),
                pgn_headers.get(constants.TAG_WHITEELO, ""),
                pgn_headers.get(constants.TAG_BLACKELO, ""),
                reference.get(constants.FILE, ""),
                reference.get(constants.GAME, ""),
            ),
            **kargs
        )
