# create_chesscalc_database.py
# Copyright 2020 Roger Marsh
# Licence: See LICENSE.txt (BSD licence)

"""Create chesscalc database with chosen database engine and segment size."""

import os
import tkinter

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
from .. import REPORT_DIRECTORY


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
            engines[unqlite_calc.unqlite_database.unqlite] = (
                unqlite_calc.Database
            )
        if vedis_calc:
            engines[vedis_calc.vedis_database.vedis] = vedis_calc.Database
        if sqlite3_calc:
            engines[sqlite3_calc.sqlite3_database.sqlite3] = (
                sqlite3_calc.Database
            )
        if apsw_calc:
            engines[apsw_calc.apsw_database.apsw] = apsw_calc.Database
        if db_calc:
            engines[db_calc.bsddb3_database.bsddb3] = db_calc.Database
        if lmdb_calc:
            engines[lmdb_calc.lmdb_database.lmdb] = lmdb_calc.Database
        if berkeleydb_calc:
            engines[berkeleydb_calc.berkeleydb_database.berkeleydb] = (
                berkeleydb_calc.Database
            )
        if dbtkinter_calc:
            engines[dbtkinter_calc.db_tkinter_database.db_tcl] = (
                dbtkinter_calc.Database
            )
        if dpt_calc:
            engines[dpt_calc.dptnofistat.dpt_database._dpt.dptapi] = (
                dpt_calc.Database
            )
        super().__init__(title="Create ChessCalc Database", engines=engines)

    def create_folder_and_database(self, event=None):
        """Delegate to superclass if directory name is allowed.

        Some directory names are reserved for specific purposes, such as
        <directory>/_reports for reports generated from the database; so
        _reports/_reports is not available as the name of a database.

        """
        path = self.directory.get()
        if os.path.split(path)[-1] == REPORT_DIRECTORY:
            tkinter.messagebox.showerror(
                parent=self.root,
                message="".join(
                    (
                        "Cannot name new performance calculation ",
                        "database directory\n\n'",
                        REPORT_DIRECTORY,
                        "'\n\nbecause\n\n'",
                        os.path.join(REPORT_DIRECTORY, REPORT_DIRECTORY),
                        "'\n\nis reserved as report directory name and ",
                        "cannot be the database file name",
                    )
                ),
            )
            return
        super().create_folder_and_database(event=event)
        if self.directory.get() == "":
            # The database directory has just been created so neither
            # exception should be raised, but ignore if one of them is
            # raised.
            try:
                if path != os.path.abspath(path):
                    path = os.path.expanduser(os.path.join("~", path))
                os.mkdir(os.path.join(path, REPORT_DIRECTORY))
            except (FileExistsError, FileNotFoundError):
                pass


if __name__ == "__main__":
    CreateChessCalcDatabase().root.mainloop()
