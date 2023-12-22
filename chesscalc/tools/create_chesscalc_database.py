# create_chesscalc_database.py
# Copyright 2020 Roger Marsh
# Licence: See LICENSE.txt (BSD licence)

"""Create chesscalc database with chosen database engine and segment size."""

from solentware_base.tools import create_database

try:
    from ..unqlite import database as unqlite_calc
except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
    unqlite_calc = None
try:
    from ..vedis import database as vedis_calc
except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
    vedis_calc = None
if create_database._deny_sqlite3:
    sqlite3_calc = None
else:
    try:
        from ..sqlite import database as sqlite3_calc
    except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
        sqlite3_calc = None
try:
    from ..apsw import database as apsw_calc
except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
    apsw_calc = None
try:
    from ..berkeleydb import database as berkeleydb_calc
except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
    berkeleydb_calc = None
try:
    from ..db import database as db_calc
except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
    db_calc = None
try:
    from ..db_tkinter import database as dbtkinter_calc
except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
    dbtkinter_calc = None
try:
    from ..dpt import database as dpt_calc
except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
    dpt_calc = None
try:
    from ..lmdb import database as lmdb_calc
except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
    lmdb_calc = None


class CreateChessCalcDatabase(create_database.CreateDatabase):
    """Create a Chess Performance Calculation database."""

    _START_TEXT = "".join(
        (
            "ChessCalc would create a new database with the top-left ",
            "engine, and segment size 4000.",
        )
    )

    def __init__(self):
        """Build the user interface."""
        engines = {}
        if unqlite_calc:
            engines[
                unqlite_calc.unqlite_database.unqlite
            ] = unqlite_calc.Database
        if vedis_calc:
            engines[vedis_calc.vedis_database.vedis] = vedis_calc.Database
        if sqlite3_calc:
            engines[
                sqlite3_calc.sqlite3_database.sqlite3
            ] = sqlite3_calc.Database
        if apsw_calc:
            engines[apsw_calc.apsw_database.apsw] = apsw_calc.Database
        if db_calc:
            engines[db_calc.bsddb3_database.bsddb3] = db_calc.Database
        if lmdb_calc:
            engines[lmdb_calc.lmdb_database.lmdb] = lmdb_calc.Database
        if berkeleydb_calc:
            engines[
                berkeleydb_calc.berkeleydb_database.berkeleydb
            ] = berkeleydb_calc.Database
        if dbtkinter_calc:
            engines[
                dbtkinter_calc.db_tkinter_database.db_tcl
            ] = dbtkinter_calc.Database
        if dpt_calc:
            engines[
                dpt_calc.dptnofistat.dpt_database._dpt.dptapi
            ] = dpt_calc.Database
        super().__init__(title="Create ChessCalc Database", engines=engines)


if __name__ == "__main__":

    CreateChessCalcDatabase().root.mainloop()
