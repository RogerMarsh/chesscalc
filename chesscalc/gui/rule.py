# rule.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Specify selection rule for games to calculate and display performances."""

import tkinter
import tkinter.ttk

from solentware_bind.gui.bindings import Bindings

from ..core.utilities import AppSysDate
from .eventspec import EventSpec
from ..core import update_database


class RuleError(Exception):
    """Raise exception in rule module."""


class Rule(Bindings):
    """Define widget to display selection rule and calculated performances."""

    def __init__(self, master, database):
        """Create the rule widget."""
        super().__init__()
        self._database = database
        self._frame = master
        entry_widgets = []
        for columnspan, column, row in (
            (4, 1, 0),
            (1, 1, 1),
            (2, 3, 1),
            (1, 1, 2),
            (1, 3, 2),
        ):
            entry_widgets.append(tkinter.ttk.Entry(master=master))
            entry_widgets[-1].grid_configure(
                column=column,
                columnspan=columnspan,
                row=row,
                sticky=tkinter.NSEW,
            )
        (
            self._rule,
            self._identity,
            self._player_name,
            self._from_date,
            self._to_date,
        ) = entry_widgets
        self._time_limits = tkinter.Text(
            master=master, height=1, wrap=tkinter.WORD
        )
        self._time_limits.grid_configure(
            column=1, columnspan=4, row=3, sticky=tkinter.EW
        )
        self._playing_mode = tkinter.Text(
            master=master, height=1, wrap=tkinter.WORD
        )
        self._playing_mode.grid_configure(
            column=1, columnspan=4, row=4, sticky=tkinter.EW
        )
        self._events = tkinter.Text(master=master, height=5, wrap=tkinter.WORD)
        self._events.grid_configure(
            column=1, columnspan=4, row=5, sticky=tkinter.EW
        )
        self._perfcalc = tkinter.Text(
            master=master, height=5, wrap=tkinter.WORD, state=tkinter.DISABLED
        )
        self._perfcalc.grid_configure(
            column=0, columnspan=5, row=7, sticky=tkinter.NSEW
        )
        for text, column, row in (
            ("Rule", 0, 0),
            ("Identity", 0, 1),
            ("Player name", 2, 1),
            ("From Date", 0, 2),
            ("To Date", 2, 2),
            ("Time controls", 0, 3),
            ("Playing modes", 0, 4),
            ("Events", 0, 5),
        ):
            tkinter.ttk.Label(master=master, text=text).grid_configure(
                column=column, row=row, padx=5
            )
        tkinter.ttk.Label(
            master=master,
            text="Performance Calculation",
            anchor=tkinter.CENTER,
        ).grid_configure(
            column=0, columnspan=5, row=6, sticky=tkinter.EW, pady=(5, 0)
        )
        master.grid_columnconfigure(0, uniform="u0")
        master.grid_columnconfigure(2, uniform="u0")
        master.grid_columnconfigure(4, weight=1, uniform="u1")
        master.grid_rowconfigure(7, weight=1, uniform="u2")

    @property
    def frame(self):
        """Return the top frame of the rule widget."""
        return self._frame

    def insert_rule(self):
        """Insert selection rule into database."""
        rule = self._rule.get().strip()
        identity = self._identity.get().strip()
        player_name = self._player_name.get().strip()
        from_date = self._from_date.get().strip()
        to_date = self._to_date.get().strip()
        events = self._events.get("1.0", tkinter.END).strip()
        if not rule:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=EventSpec.menu_selectors_insert[1],
                message="Please give a rule name for selector",
            )
            return
        if (not identity and not events) or (identity and events):
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=EventSpec.menu_selectors_insert[1],
                message="".join(
                    (
                        "Please give either a player identity, or list of ",
                        "event names and dates, but not both for selector",
                    )
                ),
            )
            return
        if identity and not identity.isdigit():
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=EventSpec.menu_selectors_insert[1],
                message="Player identity must contain digits only",
            )
            return
        if (from_date and not to_date) or (not from_date and to_date):
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=EventSpec.menu_selectors_insert[1],
                message="".join(
                    (
                        "Please give either both from date and to date, ",
                        "or neither, for selector",
                    )
                ),
            )
            return
        iso_from_date = ""
        iso_to_date = ""
        if from_date and to_date:
            appsysdate = AppSysDate()
            if appsysdate.parse_date(from_date) != len(from_date):
                tkinter.messagebox.showinfo(
                    parent=self.frame,
                    title=EventSpec.menu_selectors_insert[1],
                    message="Please give a date as 'From Date'",
                )
                return
            iso_from_date = appsysdate.iso_format_date()
            if appsysdate.parse_date(to_date) != len(to_date):
                tkinter.messagebox.showinfo(
                    parent=self.frame,
                    title=EventSpec.menu_selectors_insert[1],
                    message="Please give a date as 'To Date'",
                )
                return
            iso_to_date = appsysdate.iso_format_date()
            if len(from_date) < 11:
                tkinter.messagebox.showinfo(
                    parent=self.frame,
                    title=EventSpec.menu_selectors_insert[1],
                    message="".join(
                        (
                            "'From Date' is less than 11 characters and ",
                            "has been interpreted as '",
                            iso_from_date,
                            "' in 'yyyy-mm-dd' format",
                        )
                    ),
                )
            if len(to_date) < 11:
                tkinter.messagebox.showinfo(
                    parent=self.frame,
                    title=EventSpec.menu_selectors_insert[1],
                    message="".join(
                        (
                            "'To Date' is less than 11 characters and ",
                            "has been interpreted as '",
                            iso_to_date,
                            "' in 'yyyy-mm-dd' format",
                        )
                    ),
                )
        event_list = []
        if events:
            event_list = self._split_events(events)
            if not event_list:
                return
        if not update_database.insert_record(
            self._database,
            rule,
            identity,
            player_name,
            from_date,
            to_date,
            event_list,
        ):
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=EventSpec.menu_selectors_insert[1],
                message="Record not inserted",
            )
            return
        tkinter.messagebox.showinfo(
            parent=self.frame,
            title=EventSpec.menu_selectors_insert[1],
            message="Record inserted",
        )

    def _split_events(self, events):
        """Return list of event names and dates from events."""
        appsysdate = AppSysDate()
        event_list = []
        for count, line in enumerate(events.split(sep="\n")):
            line = line.strip()
            if not line:
                continue
            position = 0
            while True:
                match_ = appsysdate.ymd_re.search(line, position)
                if match_ is None:
                    tkinter.messagebox.showinfo(
                        parent=self.frame,
                        title=EventSpec.menu_selectors_insert[1],
                        message="".join(
                            (
                                "Date not found on line ",
                                str(count),
                                " after character ",
                                str(position),
                                " starting '",
                                line[position : position + 10],
                                "'",
                            )
                        ),
                    )
                    return None
                date = appsysdate.parse_date(match_.group())
                if date == -1:
                    tkinter.messagebox.showinfo(
                        parent=self.frame,
                        title=EventSpec.menu_selectors_insert[1],
                        message="".join(
                            (
                                "Invalid date found on line ",
                                str(count),
                                " at character ",
                                str(match_.start()),
                                " '",
                                match_.group(),
                                "'",
                            )
                        ),
                    )
                    return None
                event = [line[position : match_.start()].strip()]
                if not event[0]:
                    tkinter.messagebox.showinfo(
                        parent=self.frame,
                        title=EventSpec.menu_selectors_insert[1],
                        message="".join(
                            (
                                "No event found on line ",
                                str(count),
                                " at character ",
                                str(position),
                                " '",
                                line[position : position + 10],
                                "'",
                            )
                        ),
                    )
                    return None
                position = match_.start() + date
                event.append(appsysdate.iso_format_date())
                event_list.append(event)
                if position >= len(line):
                    break
        return event_list
