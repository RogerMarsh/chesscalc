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
from ..core import name_lookup


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
        self.time_control = None
        self.mode = None
        self.event = None
        self.player_name = None
        self.time_control_name = None
        self.mode_name = None
        self.event_names = None

    def set_values(self, *args):
        """Set state to values in *args.

        *args will usually be the values set in the rule widget when
        displayed prior to editing for updating the database.

        There must be 11 (eleven) items in *args, in order:

        rule, player_identity, from_date, to_date, time_control_identity,
        mode_identity, event_identities, player_name, time_control_name,
        mode_name, and event_names.

        """
        (
            self.rule,
            self.player,
            self.from_date,
            self.to_date,
            self.time_control,
            self.mode,
            self.event,
            self.player_name,
            self.time_control_name,
            self.mode_name,
            self.event_names,
        ) = args

    def is_changed(self, *args):
        """Return True if state is not equal the value in *args.

        *args will usually be the values in the rule widget when
        submitted for updating the database.

        There must be 11 (eleven) items in *args, in order:

        rule, player_identity, from_date, to_date, time_control_identity,
        mode_identity, event_identities, player_name, time_control_name,
        mode_name, and event_names.

        """
        return (
            self.rule,
            self.player,
            self.from_date,
            self.to_date,
            self.time_control,
            self.mode,
            self.event,
            self.player_name,
            self.time_control_name,
            self.mode_name,
            self.event_names,
        ) != args


class Rule(Bindings):
    """Define widget to display selection rule and calculated performances."""

    def __init__(self, master, database):
        """Create the rule widget."""
        super().__init__()
        self._database = database
        self._rule_record = None
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
        assert self._rule_record is None
        value = record.value
        self._enable_entry_widgets()
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
            detail = name_lookup.get_player_record_from_identity(
                self._database, value.person_identity
            )
            if detail is not None:
                self._player_name.configure(state=tkinter.NORMAL)
                self._player_name.delete("0", tkinter.END)
                self._player_name.insert(
                    tkinter.END, detail.value.alias_index_key()
                )
                self._player_name.configure(state=tkinter.DISABLED)
        if value.time_control_identity:
            detail = name_lookup.get_time_control_record_from_identity(
                self._database, value.time_control_identity
            )
            if detail is not None:
                self._time_control_name.configure(state=tkinter.NORMAL)
                self._time_control_name.delete("0", tkinter.END)
                self._time_control_name.insert(
                    tkinter.END, detail.value.alias_index_key()
                )
                self._time_control_name.configure(state=tkinter.DISABLED)
        if value.mode_identity:
            detail = name_lookup.get_mode_record_from_identity(
                self._database, value.mode_identity
            )
            if detail is not None:
                self._mode_name.configure(state=tkinter.NORMAL)
                self._mode_name.delete("0", tkinter.END)
                self._mode_name.insert(
                    tkinter.END, detail.value.alias_index_key()
                )
                self._mode_name.configure(state=tkinter.DISABLED)
        self._disable_entry_widgets()
        self._rule_record = record

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

    def get_selection_values_from_widget(self):
        """Return values in rule widget excluding performance calculation."""
        return (
            self._rule.get().strip(),
            self._player_identity.get().strip(),
            self._from_date.get().strip(),
            self._to_date.get().strip(),
            self._time_control_identity.get().strip(),
            self._mode_identity.get().strip(),
            self._event_identities.get("1.0", tkinter.END).strip(),
            self._player_name.get().strip(),
            self._time_control_name.get().strip(),
            self._mode_name.get().strip(),
            self._event_names.get("1.0", tkinter.END).strip(),
        )

    def _disable_entry_widgets(self):
        """Do nothing.

        Subclasses should override this method if entry widgets should be
        disabled at the end of populate_rule_from_record() call.

        """

    def _enable_entry_widgets(self):
        """Do nothing.

        Subclasses should override this method if entry widgets should be
        enabled at the start of populate_rule_from_record() call to allow
        changes.

        """

    def insert_rule(self):
        """Insert selection rule into database."""
        valid_values = self._validate_rule(
            *self.get_selection_values_from_widget()
        )
        if not valid_values:
            return False
        if update_database.insert_record(self._database, *valid_values):
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=EventSpec.menu_selectors_insert[1],
                message="Record inserted",
            )
            return True
        tkinter.messagebox.showinfo(
            parent=self.frame,
            title=EventSpec.menu_selectors_insert[1],
            message="Record not inserted",
        )
        return False

    def update_rule(self):
        """Update selection rule on database."""
        if self._rule_record is None:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=EventSpec.menu_selectors_update[1],
                message="Record not known, perhaps it has been deleted",
            )
            return False
        valid_values = self._validate_rule(
            *self.get_selection_values_from_widget(), insert=False
        )
        if not valid_values:
            return False
        if update_database.update_record(
            self._database, self._rule_record, *valid_values
        ):
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=EventSpec.menu_selectors_update[1],
                message="Record updated",
            )
            return True
        tkinter.messagebox.showinfo(
            parent=self.frame,
            title=EventSpec.menu_selectors_update[1],
            message="Record not updated",
        )
        return False

    def delete_rule(self):
        """Delete selection rule from database."""
        if self._rule_record is None:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=EventSpec.menu_selectors_delete[1],
                message="Record not known, perhaps already deleted",
            )
            return False
        if update_database.delete_record(self._database, self._rule_record):
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=EventSpec.menu_selectors_delete[1],
                message="Record deleted",
            )
            self._rule_record = None
            return True
        tkinter.messagebox.showinfo(
            parent=self.frame,
            title=EventSpec.menu_selectors_delete[1],
            message="Record not deleted",
        )
        return False

    def _validate_rule(
        self,
        rule,
        player_identity,
        from_date,
        to_date,
        time_control_identity,
        mode_identity,
        event_identities,
        player_name,
        time_control_name,
        mode_name,
        event_names,
        insert=True,
    ):
        """Return valid values for insert or update, or False."""
        if insert:
            title = EventSpec.menu_selectors_insert[1]
        else:
            title = EventSpec.menu_selectors_update[1]
        if not rule:
            if insert:
                message = "Please give a rule name for selector"
            else:
                message = "Cannot update because the rule has no name"
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message=message,
            )
            return False
        if (not player_identity and not event_identities) or (
            player_identity and event_identities
        ):
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="".join(
                    (
                        "Please give either a player identity, or list of ",
                        "event names and dates, but not both for selector",
                    )
                ),
            )
            return False
        if player_identity and not player_identity.isdigit():
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="Player identity must contain digits only",
            )
            return False
        if (from_date and not to_date) or (not from_date and to_date):
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="".join(
                    (
                        "Please give either both from date and to date, ",
                        "or neither, for selector",
                    )
                ),
            )
            return False
        iso_from_date = ""
        iso_to_date = ""
        if from_date and to_date:
            appsysdate = AppSysDate()
            if appsysdate.parse_date(from_date) != len(from_date):
                tkinter.messagebox.showinfo(
                    parent=self.frame,
                    title=title,
                    message="Please give a date as 'From Date'",
                )
                return False
            iso_from_date = appsysdate.iso_format_date()
            if appsysdate.parse_date(to_date) != len(to_date):
                tkinter.messagebox.showinfo(
                    parent=self.frame,
                    title=title,
                    message="Please give a date as 'To Date'",
                )
                return False
            iso_to_date = appsysdate.iso_format_date()
            if len(from_date) < 11:
                tkinter.messagebox.showinfo(
                    parent=self.frame,
                    title=title,
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
                    title=title,
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
                title=title,
                message="Time control identity must contain digits only",
            )
            return False
        if mode_identity and not mode_identity.isdigit():
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="Mode identity must contain digits only",
            )
            return False
        for event_identity in event_identities.split():
            if event_identity and not event_identity.isdigit():
                tkinter.messagebox.showinfo(
                    parent=self.frame,
                    title=title,
                    message=event_identity.join(
                        (
                            "Event identity '",
                            "' must contain digits only",
                        )
                    ),
                )
                return False
        validate = True
        messages = []
        # Assume rule name is unchanged if widget state is 'disabled'.
        if self._rule.cget("state") == tkinter.NORMAL:
            if rule != self._identity_values.rule:
                messages.append("Rule name changed")
        if player_identity:
            name = name_lookup.get_player_name_from_identity(
                self._database, player_identity
            )
            self._player_name.configure(state=tkinter.NORMAL)
            self._player_name.delete("0", tkinter.END)
            if name:
                if name != player_name:
                    messages.append("Player name changed")
                self._player_name.insert(tkinter.END, name)
            self._player_name.configure(state=tkinter.DISABLED)
            if not name:
                messages.append("Player name not found")
                validate = False
            elif not player_name:
                messages.append("Player name added")
        else:
            self._player_name.configure(state=tkinter.NORMAL)
            self._player_name.delete("0", tkinter.END)
            self._player_name.configure(state=tkinter.DISABLED)
            if player_name:
                messages.append("No player identity for name")
                validate = False
        if time_control_identity:
            name = name_lookup.get_time_control_name_from_identity(
                self._database, time_control_identity
            )
            self._time_control_name.configure(state=tkinter.NORMAL)
            self._time_control_name.delete("0", tkinter.END)
            if name:
                if name != time_control_name:
                    messages.append("Time control name changed")
                self._time_control_name.insert(tkinter.END, name)
            self._time_control_name.configure(state=tkinter.DISABLED)
            if not name:
                messages.append("Time control name not found")
                validate = False
            elif not time_control_name:
                messages.append("Time control name added")
        else:
            self._time_control_name.configure(state=tkinter.NORMAL)
            self._time_control_name.delete("0", tkinter.END)
            self._time_control_name.configure(state=tkinter.DISABLED)
            if time_control_name:
                messages.append("No time control identity for name")
                validate = False
        if mode_identity:
            name = name_lookup.get_mode_name_from_identity(
                self._database, mode_identity
            )
            self._mode_name.configure(state=tkinter.NORMAL)
            self._mode_name.delete("0", tkinter.END)
            if name:
                if name != mode_name:
                    messages.append("Mode name changed")
                self._mode_name.insert(tkinter.END, name)
            self._mode_name.configure(state=tkinter.DISABLED)
            if not name:
                messages.append("Mode name not found")
                validate = False
            elif not mode_name:
                messages.append("Mode name added")
        else:
            self._mode_name.configure(state=tkinter.NORMAL)
            self._mode_name.delete("0", tkinter.END)
            self._mode_name.configure(state=tkinter.DISABLED)
            if mode_name:
                messages.append("No mode identity for name")
                validate = False
        if event_identities:
            messages.append("Populate event names")
            if not event_names:
                validate = False
        else:
            self._event_names.configure(state=tkinter.NORMAL)
            self._event_names.delete("1.0", tkinter.END)
            self._event_names.configure(state=tkinter.DISABLED)
            if event_names:
                messages.append("No event identities for names")
                validate = False
        event_list = []
        if event_identities:
            messages.append("Events not yet implemented")
            event_list = self._split_events(event_identities, event_names)
            if not event_list:
                validate = False
        if not validate:
            if len(messages) > 1:
                messages.insert(
                    0, "At least one of the following indicates an error:\n"
                )
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="\n".join(messages),
            )
            return False
        changed = self._identity_values.is_changed(
            rule,
            player_identity,
            from_date,
            to_date,
            time_control_identity,
            mode_identity,
            event_list,
            self._player_name.get().strip(),
            self._time_control_name.get().strip(),
            self._mode_name.get().strip(),
            self._event_names.get("1.0", tkinter.END).strip(),
        )
        self._identity_values.set_values(
            rule,
            player_identity,
            from_date,
            to_date,
            time_control_identity,
            mode_identity,
            event_list,
            self._player_name.get().strip(),
            self._time_control_name.get().strip(),
            self._mode_name.get().strip(),
            self._event_names.get("1.0", tkinter.END).strip(),
        )
        if messages or changed:
            if insert:
                message_stub = " insert this new rule "
            else:
                message_stub = " update rule "
            if messages:
                messages.insert(
                    0,
                    message_stub.join(
                        ("Do you want to", "with these valid changes:\n")
                    ),
                )
            else:
                messages.append("Do you want to" + message_stub)
            if not tkinter.messagebox.askyesno(
                parent=self.frame,
                title=title,
                message="\n".join(messages),
            ):
                return False
        return (
            rule,
            player_identity,
            from_date,
            to_date,
            time_control_identity,
            mode_identity,
            event_list,
        )
