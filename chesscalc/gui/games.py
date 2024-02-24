# games.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""List the games in the database."""

from solentware_bind.gui.bindings import Bindings

from . import gamesgrid


class GamesError(Exception):
    """Raise exception in games module."""


class Games(Bindings):
    """Define widgets which list of games and PGN file references."""

    def __init__(self, master, database):
        """Create the games widget."""
        super().__init__()
        self._games_grid = gamesgrid.GamesGrid(
            parent=master, database=database
        )

    @property
    def frame(self):
        """Return the top frame of the games widget."""
        return self._games_grid.frame

    @property
    def data_grid(self):
        """Return the games widget."""
        return self._games_grid
