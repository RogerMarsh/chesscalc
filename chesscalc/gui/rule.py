# rule.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Specify selection rule for games to calculate and display performances."""

import tkinter
import tkinter.ttk

from solentware_bind.gui.bindings import Bindings

from .eventspec import EventSpec
from ..core import tab_from_selection


class RuleError(Exception):
    """Raise exception in rule module."""


class RuleIdentityValuesDisplayed:
    """Identity values set by previous validation of Rule instance.

    Database update proceeds if current validition of Rule instance
    succeeds and the current identity values are same as values here.
    """

    def __init__(self):
        """Set initial values to None."""
        self.rule = None
        self.player = None
        self.from_date = None
        self.to_date = None
        self.event = None
        self.time_control = None
        self.mode = None

    def set_values(
        self, rule, player, from_date, to_date, event, time_control, mode
    ):
        """Set values to those being validated."""
        self.rule = rule
        self.player = player
        self.from_date = from_date
        self.to_date = to_date
        self.event = event
        self.time_control = time_control
        self.mode = mode

    def is_changed(
        self, rule, player, from_date, to_date, event, time_control, mode
    ):
        """Return True if values being validated are not those here."""
        return (
            self.rule != rule
            or self.player != player
            or self.from_date != from_date
            or self.to_date != to_date
            or self.event != event
            or self.time_control != time_control
            or self.mode != mode
        )


class Rule(Bindings):
    """Define widget to display selection rule and calculated performances."""

    def __init__(self, master, database):
        """Create the rule widget."""
        super().__init__()
        self._database = database
        self._identity_values = RuleIdentityValuesDisplayed()
        self._frame = master
        entry_widgets = []
        for columnspan, column, row in (
            (4, 1, 0),
            (1, 1, 1),
            (2, 3, 1),
            (1, 1, 2),
            (1, 1, 3),
            (1, 1, 4),
            (2, 3, 4),
            (1, 1, 5),
            (2, 3, 5),
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
            self._player_identity,
            self._player_name,
            self._from_date,
            self._to_date,
            self._time_control_identity,
            self._time_control_name,
            self._mode_identity,
            self._mode_name,
        ) = entry_widgets
        self._player_name.configure(state=tkinter.DISABLED)
        self._time_control_name.configure(state=tkinter.DISABLED)
        self._mode_name.configure(state=tkinter.DISABLED)
        self._event_identities = tkinter.Text(
            master=master, height=5, width=10, wrap=tkinter.WORD
        )
        self._event_identities.grid_configure(
            column=1, columnspan=1, row=6, sticky=tkinter.EW
        )
        self._event_names = tkinter.Text(
            master=master,
            height=5,
            width=10,
            state=tkinter.DISABLED,
            background="gray85",
            wrap=tkinter.WORD,
        )
        self._event_names.grid_configure(
            column=3, columnspan=2, row=6, sticky=tkinter.EW
        )
        self._perfcalc = tkinter.Text(
            master=master,
            height=5,
            wrap=tkinter.WORD,
            background="gray93",
            state=tkinter.DISABLED,
        )
        self._perfcalc.grid_configure(
            column=0, columnspan=5, row=8, sticky=tkinter.NSEW
        )
        for text, column, row in (
            ("Rule", 0, 0),
            ("Known player identity", 0, 1),
            ("Known player name", 2, 1),
            ("From Date", 0, 2),
            ("To Date", 0, 3),
            ("Time control identity", 0, 4),
            ("Time control name", 2, 4),
            ("Mode identity", 0, 5),
            ("Mode name", 2, 5),
            ("Event identities", 0, 6),
            ("Event names", 2, 6),
        ):
            tkinter.ttk.Label(master=master, text=text).grid_configure(
                column=column, row=row, padx=5
            )
        tkinter.ttk.Label(
            master=master,
            text="Performance Calculation",
            anchor=tkinter.CENTER,
        ).grid_configure(
            column=0, columnspan=5, row=7, sticky=tkinter.EW, pady=(5, 0)
        )
        master.grid_columnconfigure(0, uniform="u0")
        master.grid_columnconfigure(2, uniform="u0")
        master.grid_columnconfigure(4, weight=1, uniform="u1")
        master.grid_rowconfigure(8, weight=1, uniform="u2")

    @property
    def frame(self):
        """Return the top frame of the rule widget."""
        return self._frame

    def _split_events(self, identities, names):
        """Return list of event identities or None."""
        identity_list = identities.split()
        for identity in identity_list:
            if identity and not identity.isdigit():
                tkinter.messagebox.showinfo(
                    parent=self.frame,
                    title=EventSpec.menu_selectors_insert[1],
                    message=identity.join(
                        (
                            "Event identity '",
                            "' must contain digits only",
                        )
                    ),
                )
                return None
        identity_lines = identities.count("\n")
        if identity_lines != len(identity_list):
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=EventSpec.menu_selectors_insert[1],
                message="".join(
                    (
                        "Event identities are not presented one ",
                        "per line.  The identities will be ",
                        "adjusted so each line has one identity.  ",
                        "The names will be adjusted to fit.",
                    )
                ),
            )
            return None
        name_lines = names.count("\n")
        if identity_lines != name_lines:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=EventSpec.menu_selectors_insert[1],
                message="".join(
                    (
                        "Number of event identities is not same ",
                        "as number of event names.  The names will be ",
                        "adjusted to fit the identities present.",
                    )
                ),
            )
            return None
        return identity_list

    def populate_rule_from_record(self, record):
        """Populate rule widget with values from record."""
        value = record.value
        self._rule.delete("0", tkinter.END)
        self._rule.insert(tkinter.END, value.name)
        self._player_identity.delete("0", tkinter.END)
        self._player_identity.insert(tkinter.END, value.person_identity)
        self._from_date.delete("0", tkinter.END)
        self._from_date.insert(tkinter.END, value.from_date)
        self._to_date.delete("0", tkinter.END)
        self._to_date.insert(tkinter.END, value.to_date)
        self._time_control_identity.delete("0", tkinter.END)
        self._time_control_identity.insert(
            tkinter.END, value.time_control_identity
        )
        self._mode_identity.delete("0", tkinter.END)
        self._mode_identity.insert(tkinter.END, value.mode_identity)
        self._event_identities.delete("1.0", tkinter.END)
        self._event_identities.insert(
            tkinter.END, "\n".join(value.event_identities)
        )
        if value.person_identity:
            detail = tab_from_selection.get_person_detail(
                value.person_identity, self._database
            )
            self._player_name.configure(state=tkinter.NORMAL)
            self._player_name.delete("0", tkinter.END)
            self._player_name.insert(
                tkinter.END, detail.value.alias_index_key()
            )
            self._player_name.configure(state=tkinter.DISABLED)
        if value.time_control_identity:
            detail = tab_from_selection.get_time_control_detail(
                value.time_control_identity, self._database
            )
            self._time_control_name.configure(state=tkinter.NORMAL)
            self._time_control_name.delete("0", tkinter.END)
            self._time_control_name.insert(
                tkinter.END, detail.value.alias_index_key()
            )
            self._time_control_name.configure(state=tkinter.DISABLED)
        if value.mode_identity:
            detail = tab_from_selection.get_mode_detail(
                value.mode_identity, self._database
            )
            self._mode_name.configure(state=tkinter.NORMAL)
            self._mode_name.delete("0", tkinter.END)
            self._mode_name.insert(tkinter.END, detail.value.alias_index_key())
            self._mode_name.configure(state=tkinter.DISABLED)

    def populate_rule_person_from_record(self, record):
        """Populate rule widget person with values from record."""
        value = record.value
        self._player_identity.delete("0", tkinter.END)
        self._player_identity.insert(tkinter.END, value.identity)
        self._player_name.configure(state=tkinter.NORMAL)
        self._player_name.delete("0", tkinter.END)
        self._player_name.insert(tkinter.END, value.alias_index_key())
        self._player_name.configure(state=tkinter.DISABLED)

    def populate_rule_time_control_from_record(self, record):
        """Populate rule widget time control with values from record."""
        value = record.value
        self._time_control_identity.delete("0", tkinter.END)
        self._time_control_identity.insert(tkinter.END, value.identity)
        self._time_control_name.configure(state=tkinter.NORMAL)
        self._time_control_name.delete("0", tkinter.END)
        self._time_control_name.insert(tkinter.END, value.alias_index_key())
        self._time_control_name.configure(state=tkinter.DISABLED)

    def populate_rule_mode_from_record(self, record):
        """Populate rule widget mode with values from record."""
        value = record.value
        self._mode_identity.delete("0", tkinter.END)
        self._mode_identity.insert(tkinter.END, value.identity)
        self._mode_name.configure(state=tkinter.NORMAL)
        self._mode_name.delete("0", tkinter.END)
        self._mode_name.insert(tkinter.END, value.alias_index_key())
        self._mode_name.configure(state=tkinter.DISABLED)
