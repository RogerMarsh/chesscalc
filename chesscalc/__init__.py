# __init__.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Calculate player's performances on a set of games.

Performances are calculated by iteration where each player starts with 0 as
their performance.  The scale used is +50 for a win, -50 for a loss, and 0 for
a draw, relative to the opponents performance.  English Chess Federation (ECF)
grades have the same scale.

The performances are not grades because the results of calculations in previous
runs are not used in this calculation.

"""
import solentware_base.core.constants as sb_c_constants

APPLICATION_NAME = "ChessPerfCalc"
ERROR_LOG = "ErrorLog"

# Map database module names to application module
APPLICATION_DATABASE_MODULE = {
    sb_c_constants.BERKELEYDB_MODULE: __name__ + ".berkeleydb.database",
    sb_c_constants.BSDDB3_MODULE: __name__ + ".db.database",
    sb_c_constants.SQLITE3_MODULE: __name__ + ".sqlite.database",
    sb_c_constants.APSW_MODULE: __name__ + ".apsw.database",
    sb_c_constants.DPT_MODULE: __name__ + ".dpt.database",
    sb_c_constants.UNQLITE_MODULE: __name__ + ".unqlite.database",
    sb_c_constants.VEDIS_MODULE: __name__ + ".vedis.database",
    sb_c_constants.DB_TCL_MODULE: __name__ + ".db_tkinter.database",
    sb_c_constants.LMDB_MODULE: __name__ + ".lmdb.database",
}

del sb_c_constants
