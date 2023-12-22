# timecontrolsgrid.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Chess performance database datagrid class for time controls."""

import tkinter

from solentware_grid import datagrid
from solentware_grid.core import dataclient
from solentware_grid.gui import gridbindings

from . import timecontrolsrow
from ..core import filespec


class TimeControlsGrid(gridbindings.GridBindings, datagrid.DataGridReadOnly):
    """Grid for list of time control details in games from PGN files."""

    def __init__(self, database=None, **kwargs):
        """Extend and note sibling grids."""
        super().__init__(**kwargs)
        self.bindings()
        self.make_header(timecontrolsrow.TimeControlsRow.header_specification)
        source = dataclient.DataSource(
            database,
            filespec.TIME_FILE_DEF,
            filespec.TIME_ALIAS_FIELD_DEF,
            timecontrolsrow.TimeControlsRow,
        )
        self.set_data_source(source)

        # Not using appsys* modules: so how does chesstab do this if needed?
        # self.appsyspanel.get_appsys().get_data_register().register_in(
        #    self, self.on_data_change
        # )

    def show_popup_menu_no_row(self, event=None):
        """Override superclass to do nothing."""
        # Added when DataGridBase changed to assume a popup menu is available
        # when right-click done on empty part of data drid frame.  The popup is
        # used to show all navigation available from grid: but this is not done
        # in chesscalc, at least yet, so avoid the temporary loss of focus to
        # an empty popup menu.
