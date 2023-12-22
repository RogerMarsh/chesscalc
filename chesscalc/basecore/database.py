# database.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Database methods common to all database engine interfaces."""

import os
import shutil

from .. import APPLICATION_NAME, ERROR_LOG


class Database:
    """Provide methods common to all database engine interfaces."""

    def use_deferred_update_process(self):
        """Return path to deferred update module."""
        return self._deferred_update_process

    def open_database(self, files=None):
        """Return '' to fit behaviour of dpt version of this method."""
        super().open_database(files=files)
        return ""

    def delete_database(self, names):
        """Delete results database and return message about items not deleted."""
        listnames = set(n for n in os.listdir(self.home_directory))
        homenames = set(n for n in names if os.path.basename(n) in listnames)
        if ERROR_LOG in listnames:
            homenames.add(os.path.join(self.home_directory, ERROR_LOG))
        if len(listnames - set(os.path.basename(h) for h in homenames)):
            message = "".join(
                (
                    "There is at least one file or folder in\n\n",
                    self.home_directory,
                    "\n\nwhich may not be part of the database.  These items ",
                    "have not been deleted by ",
                    APPLICATION_NAME,
                    ".",
                )
            )
        else:
            message = None
        self.close_database()
        for h in homenames:
            if os.path.isdir(h):
                shutil.rmtree(h, ignore_errors=True)
            else:
                os.remove(h)
        try:
            os.rmdir(self.home_directory)
        except:
            pass
        return message
