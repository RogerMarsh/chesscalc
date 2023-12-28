# ruleedit.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Customize rule.Rule for insrtion of new rule into calculations list."""

import tkinter
import tkinter.ttk

from . import rule
from ..core.utilities import AppSysDate
from .eventspec import EventSpec
from ..core import update_database
from ..core import name_lookup


class RuleEdit(rule.Rule):
    """Define widget to insert selection rule and calculated performances."""

    def __init__(self, *args):
        """Create the rule widget."""
        super().__init__(*args)

    def insert_rule(self):
        """Insert selection rule into database."""
        rule = self._rule.get().strip()
        player_identity = self._player_identity.get().strip()
        from_date = self._from_date.get().strip()
        to_date = self._to_date.get().strip()
        time_control_identity = self._time_control_identity.get().strip()
        mode_identity = self._mode_identity.get().strip()
        event_identities = self._event_identities.get(
            "1.0", tkinter.END
        ).strip()
        if not rule:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=EventSpec.menu_selectors_insert[1],
                message="Please give a rule name for selector",
            )
            return
        if (not player_identity and not event_identities) or (
            player_identity and event_identities
        ):
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
        if player_identity and not player_identity.isdigit():
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
        if time_control_identity and not time_control_identity.isdigit():
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=EventSpec.menu_selectors_insert[1],
                message="Time control identity must contain digits only",
            )
            return
        if mode_identity and not mode_identity.isdigit():
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=EventSpec.menu_selectors_insert[1],
                message="Mode identity must contain digits only",
            )
            return
        for event_identity in event_identities.split():
            if event_identity and not event_identity.isdigit():
                tkinter.messagebox.showinfo(
                    parent=self.frame,
                    title=EventSpec.menu_selectors_insert[1],
                    message=event_identity.join(
                        (
                            "Event identity '",
                            "' must contain digits only",
                        )
                    ),
                )
                return
        player_name = self._player_name.get().strip()
        time_control_name = self._time_control_name.get().strip()
        mode_name = self._mode_name.get().strip()
        event_names = self._event_names.get("1.0", tkinter.END).strip()
        validate = True
        if player_identity:
            name = name_lookup.get_player_name_from_identity(
                self._database, player_identity
            )
            self._player_name.configure(state=tkinter.NORMAL)
            self._player_name.delete("0", tkinter.END)
            if name:
                if name != player_name:
                    validate = False
                self._player_name.insert(tkinter.END, name)
            self._player_name.configure(state=tkinter.DISABLED)
            if not name:
                tkinter.messagebox.showinfo(
                    parent=self.frame,
                    title=EventSpec.menu_selectors_insert[1],
                    message="Player name not found",
                )
                validate = False
            elif not player_name:
                validate = False
        else:
            self._player_name.configure(state=tkinter.NORMAL)
            self._player_name.delete("0", tkinter.END)
            self._player_name.configure(state=tkinter.DISABLED)
            if player_name:
                validate = False
        if time_control_identity:
            name = name_lookup.get_time_control_name_from_identity(
                self._database, time_control_identity
            )
            self._time_control_name.configure(state=tkinter.NORMAL)
            self._time_control_name.delete("0", tkinter.END)
            if name:
                if name != time_control_name:
                    validate = False
                self._time_control_name.insert(tkinter.END, name)
            self._time_control_name.configure(state=tkinter.DISABLED)
            if not name:
                tkinter.messagebox.showinfo(
                    parent=self.frame,
                    title=EventSpec.menu_selectors_insert[1],
                    message="Time control name not found",
                )
                validate = False
            elif not time_control_name:
                validate = False
        else:
            self._time_control_name.configure(state=tkinter.NORMAL)
            self._time_control_name.delete("0", tkinter.END)
            self._time_control_name.configure(state=tkinter.DISABLED)
            if time_control_name:
                validate = False
        if mode_identity:
            name = name_lookup.get_mode_name_from_identity(
                self._database, mode_identity
            )
            self._mode_name.configure(state=tkinter.NORMAL)
            self._mode_name.delete("0", tkinter.END)
            if name:
                if name != mode_name:
                    validate = False
                self._mode_name.insert(tkinter.END, name)
            self._mode_name.configure(state=tkinter.DISABLED)
            if not name:
                tkinter.messagebox.showinfo(
                    parent=self.frame,
                    title=EventSpec.menu_selectors_insert[1],
                    message="Mode name not found",
                )
                validate = False
            elif not mode_name:
                validate = False
        else:
            self._mode_name.configure(state=tkinter.NORMAL)
            self._mode_name.delete("0", tkinter.END)
            self._mode_name.configure(state=tkinter.DISABLED)
            if mode_name:
                validate = False
        if event_identities:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=EventSpec.menu_selectors_insert[1],
                message="Populate event names",
            )
            if not event_names:
                validate = False
        else:
            self._event_names.configure(state=tkinter.NORMAL)
            self._event_names.delete("1.0", tkinter.END)
            self._event_names.configure(state=tkinter.DISABLED)
            if event_names:
                validate = False
        if not validate:
            return
        event_list = []
        if event_identities:
            event_list = self._split_events(event_identities, event_names)
            if not event_list:
                return
        changed = self._identity_values.is_changed(
            rule,
            player_identity,
            from_date,
            to_date,
            event_list,
            time_control_identity,
            mode_identity,
        )
        self._identity_values.set_values(
            rule,
            player_identity,
            from_date,
            to_date,
            event_list,
            time_control_identity,
            mode_identity,
        )
        if changed:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=EventSpec.menu_selectors_insert[1],
                message="".join(
                    (
                        "Changed identities are valid: please repeat ",
                        "action to insert rule",
                    )
                ),
            )
            return
        changed = update_database.insert_record(
            self._database,
            rule,
            player_identity,
            from_date,
            to_date,
            event_list,
            time_control_identity,
            mode_identity,
        )
        if changed:
            message = "Record inserted"
        else:
            message = "Record not inserted"
        tkinter.messagebox.showinfo(
            parent=self.frame,
            title=EventSpec.menu_selectors_insert[1],
            message=message,
        )
