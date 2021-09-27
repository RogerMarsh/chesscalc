# help.py
# Copyright 2009 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Functions to create Help widgets for performance calculations.

"""

import tkinter

import solentware_misc.gui.textreadonly
from solentware_misc.gui.help import help_widget

import chesscalc.help


def help_about_calculator(master):
    """Display About document for ChessPerfCalc."""

    help_widget(master, chesscalc.help.ABOUT, chesscalc.help)


def help_notes_calculator(master):
    """Display Notes document for ChessPerfCalc."""

    help_widget(master, chesscalc.help.NOTES, chesscalc.help)


if __name__ == "__main__":
    # Display all help documents without running ChessResults application

    root = tkinter.Tk()
    help_about_calculator(root)
    help_notes_calculator(root)
    root.mainloop()
