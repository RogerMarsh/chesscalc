# rule.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Specify selection rule for games to calculate and display performances."""

import tkinter
import tkinter.ttk
import ast

from solentware_bind.gui.bindings import Bindings

from ..core.utilities import AppSysDate
from .eventspec import EventSpec
from ..core import update_database
from ..core import name_lookup
from ..core import calculate
from ..core import filespec
from ..core import performancerecord


class PopulatePerson(Exception):
    """Raise exception if no record for person identity."""


class PopulateTimeControl(Exception):
    """Raise exception if no record for time control identity."""


class PopulateMode(Exception):
    """Raise exception if no record for mode identity."""


class PopulateEvent(Exception):
    """Raise exception if no record for event identity."""


class NonCalculableSortKey(Exception):
    """Raise exception if no record for person identity for sort key."""


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
        self._rule = _create_entry_widget(4, 1, 0, master)
        self._player_identity = _create_entry_widget(1, 1, 1, master)
        self._player_name = _create_entry_widget(2, 3, 1, master)
        self._from_date = _create_entry_widget(1, 1, 2, master)
        self._to_date = _create_entry_widget(1, 1, 3, master)
        self._time_control_identity = _create_entry_widget(1, 1, 4, master)
        self._time_control_name = _create_entry_widget(2, 3, 4, master)
        self._mode_identity = _create_entry_widget(1, 1, 5, master)
        self._mode_name = _create_entry_widget(2, 3, 5, master)
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
        if value.event_identities:
            self._event_names.configure(state=tkinter.NORMAL)
            self._event_names.delete("1.0", tkinter.END)
            for event_identity in value.event_identities:
                detail = name_lookup.get_event_record_from_identity(
                    self._database, event_identity
                )
                if detail is not None:
                    self._event_names.insert(
                        tkinter.END, detail.value.alias_index_key()
                    )
                self._event_names.insert(tkinter.END, "\n")
            self._event_names.configure(state=tkinter.DISABLED)
        self._disable_entry_widgets()
        self._rule_record = record

    def populate_rule_person_from_record(self, record):
        """Populate rule widget person with values from record."""
        if record is None:
            raise PopulatePerson("No person record")
        value = record.value
        self._player_identity.delete("0", tkinter.END)
        self._player_identity.insert(tkinter.END, value.identity)
        self._player_name.configure(state=tkinter.NORMAL)
        self._player_name.delete("0", tkinter.END)
        self._player_name.insert(tkinter.END, value.alias_index_key())
        self._player_name.configure(state=tkinter.DISABLED)

    def populate_rule_events_from_records(self, records):
        """Populate rule widget events with values from records."""
        self._event_identities.delete("1.0", tkinter.END)
        self._event_names.configure(state=tkinter.NORMAL)
        self._event_names.delete("1.0", tkinter.END)
        for record in records:
            if record is None:
                raise PopulateEvent("No event record for one of events")
            value = record.value
            self._event_identities.insert(tkinter.END, value.identity)
            self._event_identities.insert(tkinter.END, "\n")
            self._event_names.insert(tkinter.END, value.alias_index_key())
            self._event_names.insert(tkinter.END, "\n")
        self._event_names.configure(state=tkinter.DISABLED)

    def populate_rule_time_control_from_record(self, record):
        """Populate rule widget time control with values from record."""
        if record is None:
            raise PopulateTimeControl("No time control record")
        value = record.value
        self._time_control_identity.delete("0", tkinter.END)
        self._time_control_identity.insert(tkinter.END, value.identity)
        self._time_control_name.configure(state=tkinter.NORMAL)
        self._time_control_name.delete("0", tkinter.END)
        self._time_control_name.insert(tkinter.END, value.alias_index_key())
        self._time_control_name.configure(state=tkinter.DISABLED)

    def populate_rule_mode_from_record(self, record):
        """Populate rule widget mode with values from record."""
        if record is None:
            raise PopulateMode("No mode record")
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

    def calulate_performances_for_rule(self):
        """Calculate performances for selection rule on database."""
        if self._rule_record is None:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=EventSpec.menu_calculate_calculate[1],
                message="Record not known, perhaps it has been deleted",
            )
            return False
        valid_values = self._extract_rule(
            *self.get_selection_values_from_widget()
        )
        if not valid_values:
            return False
        calculation = calculate.calculate(self._database, *valid_values)
        if calculation is None:
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=EventSpec.menu_selectors_update[1],
                message="Performances not calculated",
            )
            return False
        generate_report(calculation, self._perfcalc, self._database)
        tkinter.messagebox.showinfo(
            parent=self.frame,
            title=EventSpec.menu_calculate_calculate[1],
            message="Performances calculated",
        )
        return True

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
        event_identity_list = []
        event_name_list = []
        if event_identities:
            for identity in event_identities.split():
                name = name_lookup.get_event_name_from_identity(
                    self._database, identity
                )
                if name is None:
                    messages.append(
                        identity.join(
                            (
                                "Name not found for identity '",
                                "', perhaps it is not the alias too",
                            )
                        )
                    )
                    validate = False
                event_identity_list.append(identity)
                event_name_list.append(name)
            self._event_names.configure(state=tkinter.NORMAL)
            self._event_names.delete("1.0", tkinter.END)
            if event_name_list:
                if event_name_list != event_names.strip("\n").split("\n"):
                    messages.append("At least one event name changed")
                self._event_names.insert(
                    tkinter.END, "\n".join(event_name_list)
                )
            self._event_names.configure(state=tkinter.DISABLED)
        else:
            self._event_names.configure(state=tkinter.NORMAL)
            self._event_names.delete("1.0", tkinter.END)
            self._event_names.configure(state=tkinter.DISABLED)
            if event_names:
                messages.append("No event identities for names")
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
            event_identity_list,
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
            event_identity_list,
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
            [
                item[-1]
                for item in sorted(zip(event_name_list, event_identity_list))
            ],
        )

    def _extract_rule(
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
    ):
        """Return valid values for insert or update, or False."""
        title = EventSpec.menu_calculate_calculate[1]
        if (not player_identity and not event_identities) or (
            player_identity and event_identities
        ):
            tkinter.messagebox.showinfo(
                parent=self.frame,
                title=title,
                message="".join(
                    (
                        "Performance calculation needs either a player ",
                        "identity, or list of event names, but not both.",
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
        event_identity_list = []
        event_name_list = []
        if event_identities:
            for identity in event_identities.split():
                name = name_lookup.get_event_name_from_identity(
                    self._database, identity
                )
                if name is None:
                    messages.append(
                        identity.join(
                            (
                                "Name not found for identity '",
                                "', perhaps it is not the alias too",
                            )
                        )
                    )
                    validate = False
                event_identity_list.append(identity)
                event_name_list.append(name)
            self._event_names.configure(state=tkinter.NORMAL)
            self._event_names.delete("1.0", tkinter.END)
            if event_name_list:
                if event_name_list != event_names.strip("\n").split("\n"):
                    messages.append("At least one event name changed")
                self._event_names.insert(
                    tkinter.END, "\n".join(event_name_list)
                )
            self._event_names.configure(state=tkinter.DISABLED)
        else:
            self._event_names.configure(state=tkinter.NORMAL)
            self._event_names.delete("1.0", tkinter.END)
            self._event_names.configure(state=tkinter.DISABLED)
            if event_names:
                messages.append("No event identities for names")
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
            event_identity_list,
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
            event_identity_list,
            self._player_name.get().strip(),
            self._time_control_name.get().strip(),
            self._mode_name.get().strip(),
            self._event_names.get("1.0", tkinter.END).strip(),
        )
        if messages or changed:
            message_stub = " calculate performances "
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
            [
                item[-1]
                for item in sorted(zip(event_name_list, event_identity_list))
            ],
        )


def generate_report(calulation, report_widget, database):
    """Generate calculation report from database in report_widget."""
    convergent_populations = calulation.populations
    non_convergent_populations = calulation.non_convergent_populations
    non_calculable_populations = calulation.non_calculable_populations
    report_widget.configure(state=tkinter.NORMAL)
    report_widget.delete("1.0", tkinter.END)
    if len(convergent_populations) + len(non_convergent_populations) == 0:
        report_widget.insert(
            tkinter.END,
            "There are no populations with calculated performances.\n\n",
        )
    elif len(convergent_populations) + len(non_convergent_populations) == 1:
        report_widget.insert(
            tkinter.END,
            "There is one population with calculated performances.\n\n",
        )
    else:
        report_widget.insert(
            tkinter.END,
            "".join(
                (
                    "There are ",
                    str(
                        len(convergent_populations)
                        + len(non_convergent_populations)
                    ),
                    " populations with calculated performances.\n\n",
                )
            ),
        )
    if len(non_convergent_populations) == 0:
        report_widget.insert(
            tkinter.END,
            "".join(
                (
                    "No populations need 'three dummy players' to ",
                    "enable performance calculation.\n\n",
                )
            ),
        )
    elif len(non_convergent_populations) == 1:
        report_widget.insert(
            tkinter.END,
            "".join(
                (
                    "One population needs 'three dummy players' to ",
                    "enable performance calculation.\n\n",
                )
            ),
        )
    else:
        report_widget.insert(
            tkinter.END,
            "".join(
                (
                    str(len(non_convergent_populations)),
                    " populations need 'three dummy players' to ",
                    "enable performance calculation.\n\n",
                )
            ),
        )
    if len(non_calculable_populations) == 0:
        report_widget.insert(
            tkinter.END,
            "".join(
                (
                    "There are no populations without calculated ",
                    "performances.\n\n",
                )
            ),
        )
    elif len(non_calculable_populations) == 1:
        report_widget.insert(
            tkinter.END,
            "".join(
                (
                    "There is one population without calculated ",
                    "performances.\n\n",
                )
            ),
        )
    else:
        report_widget.insert(
            tkinter.END,
            "".join(
                (
                    "There are ",
                    str(len(non_calculable_populations)),
                    " populations without calculated performances.\n\n",
                )
            ),
        )
    count = 0
    for populations in (convergent_populations, non_convergent_populations):
        for performance_population in populations:
            count += 1
            high_performance = performance_population.high_performance
            report_widget.insert(
                tkinter.END,
                "".join(
                    (
                        "Performances (0 is best) in population ",
                        str(count),
                        " sorted by player name:\n\n",
                    )
                ),
            )
            for player in sorted(
                performance_population.persons.values(),
                key=lambda person: person.name.lower(),
            ):
                report_widget.insert(
                    tkinter.END,
                    "".join(
                        (
                            player.name,
                            "\t\t\t",
                            str(player.normal_performance(high_performance)),
                            "\n",
                        )
                    ),
                )
            report_widget.insert(tkinter.END, "\n")
            report_widget.insert(
                tkinter.END,
                "".join(
                    (
                        "Performances in population ",
                        str(count),
                        " sorted by performance (0 is best):\n\n",
                    )
                ),
            )
            for player in sorted(
                performance_population.persons.values(),
                key=lambda person: (-person.performance, person.name.lower()),
            ):
                report_widget.insert(
                    tkinter.END,
                    "".join(
                        (
                            str(player.normal_performance(high_performance)),
                            "\t",
                            player.name,
                            "\n",
                        )
                    ),
                )
            report_widget.insert(tkinter.END, "\n")
    for count, non_calculable in enumerate(non_calculable_populations):
        report_widget.insert(
            tkinter.END,
            "".join(
                (
                    "Players in population ",
                    str(count + 1),
                    " where performance calculation not done:\n\n",
                )
            ),
        )
        lookup = {}
        for player in sorted(
            non_calculable.persons.values(),
            key=lambda person: _non_calculable_sort_key(
                person, database, lookup
            ),
        ):
            fields = lookup[player.code]
            report_widget.insert(
                tkinter.END,
                "".join(
                    (
                        fields[0],
                        "\t\t\t\t",
                        fields[1],
                        "\t\t\t\t",
                        fields[2],
                        "\n",
                    )
                ),
            )
        report_widget.insert(tkinter.END, "\n")
    report_widget.configure(state=tkinter.DISABLED)


def _create_entry_widget(columnspan, column, row, master):
    """Return Entry in master over columnspan columns at column row."""
    widget = tkinter.ttk.Entry(master=master)
    widget.grid_configure(
        column=column,
        columnspan=columnspan,
        row=row,
        sticky=tkinter.NSEW,
    )
    return widget


def _non_calculable_sort_key(player, database, lookup):
    """Return sort key for non-calculable performance population reports.

    The value for player from database, from which sort key is derived,
    is stored in lookup.  The sort key is the lower-case version of this
    value.

    The value in lookup is put in the report (by the caller).

    """
    person_record = performancerecord.PlayerDBrecord()
    playerset = database.recordlist_key(
        filespec.PLAYER_FILE_DEF,
        filespec.PLAYER_UNIQUE_FIELD_DEF,
        key=database.encode_record_selector(player.code),
    )
    person_cursor = database.database_cursor(
        filespec.PLAYER_FILE_DEF, None, recordset=playerset
    )
    record = person_cursor.first()
    if record is None:
        raise NonCalculableSortKey(
            "No record found for player code " + str(player.code)
        )
    person_record.load_record(record)
    value = person_record.value
    lookup[value.identity] = tuple(
        field for field in ast.literal_eval(value.alias_index_key())[:3]
    )
    return tuple(field.lower() for field in lookup[value.identity])
