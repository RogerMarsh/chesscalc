# calculator.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Chess Performance Calculation application."""
import os
import tkinter
import tkinter.ttk
import tkinter.messagebox
import tkinter.filedialog
import multiprocessing

from solentware_bind.gui.bindings import Bindings
from solentware_bind.gui.exceptionhandler import ExceptionHandler

from solentware_base import modulequery

from .. import APPLICATION_NAME
from . import help_
from .eventspec import EventSpec
from ..core import configuration
from ..core import constants
from ..core import filespec
from .. import APPLICATION_DATABASE_MODULE, ERROR_LOG
from ..shared import rundu
from . import games
from . import players
from . import persons
from . import events
from . import timecontrols
from . import modes
from . import selectors
from . import rule
from ..core import identity


ExceptionHandler.set_application_name(APPLICATION_NAME)

STARTUP_MINIMUM_WIDTH = 380
STARTUP_MINIMUM_HEIGHT = 400
_MENU_SEPARATOR = (None, None)

_HELP_TEXT = "".join(
    (
        "Performance calculations are based on either a particular ",
        "player or a list of events.\n\n",
        "Games are included only if they are associated with a player ",
        "entry listed on the 'Identified players' tab.  This lists ",
        "the same entries as the right-hand list of the 'New players' ",
        "tab.  Games associated with player entries on the left-hand ",
        "list of the 'New players' tab are not included.\n\n",
        "The tabs are displayed when a database is open.  Games are ",
        "imported from PGN files and added to the 'Games' tab.  The ",
        "players in these games are added to the left-hand list of ",
        "the 'New players' tab.  Event details which influence ",
        "performance calculations are added to the 'Events', 'Time ",
        "controls', and 'Modes' tabs.\n\n",
        "The available performance calculation rules are listed on the ",
        "'Calculations' tab.  New rules are added by the 'Selectors | "
        "New Rule' action: a blank 'New Rule' tab is shown by default, ",
        "but values can be set by selecting and bookmarking entries ",
        "on the 'Identified players', 'Events', 'Time controls', and ",
        "'Mode' tabs.\n\n\n",
        "A date range for a player limits the games used in the ",
        "calculation to all games played in that range by the player ",
        "and opponents, and opponents of oppenents, and so on.\n\n",
        "A list of events without a date range does a performance ",
        "calculation on just the games in the events.\n\n",
        "A date range for a list of events includes all games played ",
        "between those dates by the players in the events.  Games ",
        "played by their opponents outside the selected events are ",
        "not included.\n\n\n",
        "A player is selected by identity number.  The name associated ",
        "with the identity on the 'Identified players' tab must be the one ",
        "given as name on the 'New Rule' tab.\n\n",
        "The games of all players whose alias matches the given ",
        "identity number are included.  Often it will be clear the ",
        "aliases refer to the same person: they have the same FIDE ",
        "number perhaps.\n\n\n",
        "PGN headers with the same values of FideId, Name, Event, ",
        "EventDate, Section, Stage, and Team, are assumed to refer to ",
        "the same player.  Some of these headers have 'Black' and ",
        "'White' versions.\n\n",
        "Otherwise, PGN headers which differ are taken to refer to ",
        "the same player only if the 'Player identity | Identify' action ",
        "is applied on the 'New players' tab.\n\n\n",
        "Identifications can be undone by the 'Player identity | ",
        "Break selected' and 'Player identity | Split All' actions on the "
        "'Identified players' tab.\n\n\n",
        "Event, time control, and playing mode entries can be identified ",
        "as references to the same thing by the relevant 'Identify ...' ",
        "action in the 'Other identities' menu.\n\n",
        ""
    )
)


class CalculatorError(Exception):
    """Exception class fo chess module."""


class CalculatorStartSubprocessError(Exception):
    """Exception class fo chess module."""


class _Import:
    """Names of classes imported by import_module from alternative modules.

    For runtime "from database import Database" and similar.

    Class attribute rather than module constant to fit default naming style
    which does not attract a comment from pylint.
    """

    Database = "Database"


class Calculator(Bindings):
    """Base class for reports and dialogues."""

    def __init__(self, **kargs):
        """Create widget to display performance calculations for games."""
        super().__init__()
        self._database_kargs = kargs
        self._database_class = None
        self._database_enginename = None
        self._database_modulename = None
        self.database = None
        self.database_folder = None
        self._pgn_directory = None
        self._import_subprocess = None
        self._notebook = None
        self._games_tab = None
        self._players_tab = None
        self._persons_tab = None
        self._calculations_tab = None
        self._events_tab = None
        self._time_limits_tab = None
        self._modes_tab = None
        self._calculations_tab = None
        self._rule_tabs = {}
        self._games = None
        self._players = None
        self._persons = None
        self._events = None
        self._time_limits = None
        self._modes = None
        self._selectors = None
        self.widget = tkinter.Tk()
        try:
            self._initialize()
        except Exception as exc:
            self.widget.destroy()
            del self.widget
            # pylint message broad-except.
            # Can keep going for some exceptions.
            raise CalculatorError(
                " initialize ".join(("Unable to ", APPLICATION_NAME))
            ) from exc

    def _initialize(self):
        """Build widget to display performance calculations for games."""
        self.widget.wm_title("Performance Calculation")
        self.widget.wm_minsize(
            width=STARTUP_MINIMUM_WIDTH, height=STARTUP_MINIMUM_HEIGHT
        )
        menubar = tkinter.Menu(master=self.widget)
        self.widget.configure(menu=menubar)
        menu1 = tkinter.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Database", menu=menu1, underline=0)
        menu2 = tkinter.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Player identity", menu=menu2, underline=0)
        menu3 = tkinter.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Other identities", menu=menu3, underline=0)
        menu31 = tkinter.Menu(menu3, tearoff=False)
        menu32 = tkinter.Menu(menu3, tearoff=False)
        menu4 = tkinter.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Selectors", menu=menu4, underline=0)
        menuh = tkinter.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Help", menu=menuh, underline=0)
        for menu, accelerator, function in (
            (menu1,) + _MENU_SEPARATOR,
            (menu1, EventSpec.menu_database_open, self.database_open),
            (menu1, EventSpec.menu_database_new, self.database_new),
            (menu1, EventSpec.menu_database_close, self.database_close),
            (menu1,) + _MENU_SEPARATOR,
            (menu1, EventSpec.menu_database_import, self.database_import),
            (menu1, EventSpec.menu_database_verify, self.database_verify),
            (menu1,) + _MENU_SEPARATOR,
            (menu1, EventSpec.menu_database_delete, self.database_delete),
            (menu1,) + _MENU_SEPARATOR,
            (menu1, EventSpec.menu_database_quit, self.database_quit),
            (menu1,) + _MENU_SEPARATOR,
            (menu2,) + _MENU_SEPARATOR,
            (menu2, EventSpec.menu_player_identify, self.player_identify),
            (menu2,) + _MENU_SEPARATOR,
            (menu2, EventSpec.menu_player_break, self.player_break),
            (menu2, EventSpec.menu_player_split, self.player_split),
            (menu2, EventSpec.menu_player_change, self.player_change),
            (menu2,) + _MENU_SEPARATOR,
            (menu3,) + _MENU_SEPARATOR,
            (menu3, EventSpec.menu_other_event_identify, self.event_identify),
            (menu3,) + _MENU_SEPARATOR,
            (menu3, EventSpec.menu_other_event_break, self.event_break),
            (menu3, EventSpec.menu_other_event_split, self.event_split),
            (menu3, EventSpec.menu_other_event_change, self.event_change),
            (menu3,) + _MENU_SEPARATOR,
            (menu31,) + _MENU_SEPARATOR,
            (menu31, EventSpec.menu_other_time_identify, self.time_identify),
            (menu31,) + _MENU_SEPARATOR,
            (menu31, EventSpec.menu_other_time_break, self.time_break),
            (menu31, EventSpec.menu_other_time_split, self.time_split),
            (menu31, EventSpec.menu_other_time_change, self.time_change),
            (menu31,) + _MENU_SEPARATOR,
            (menu32,) + _MENU_SEPARATOR,
            (menu32, EventSpec.menu_other_mode_identify, self.mode_identify),
            (menu32,) + _MENU_SEPARATOR,
            (menu32, EventSpec.menu_other_mode_break, self.mode_break),
            (menu32, EventSpec.menu_other_mode_split, self.mode_split),
            (menu32, EventSpec.menu_other_mode_change, self.mode_change),
            (menu32,) + _MENU_SEPARATOR,
            (menu4,) + _MENU_SEPARATOR,
            (menu4, EventSpec.menu_selectors_new, self.selectors_new),
            (menu4, EventSpec.menu_selectors_show, self.selectors_show),
            (menu4, EventSpec.menu_selectors_edit, self.selectors_edit),
            (menu4,) + _MENU_SEPARATOR,
            (menu4, EventSpec.menu_selectors_insert, self.selectors_insert),
            (menu4, EventSpec.menu_selectors_update, self.selectors_update),
            (menu4, EventSpec.menu_selectors_delete, self.selectors_delete),
            (menu4,) + _MENU_SEPARATOR,
            (menu4, EventSpec.menu_selectors_close, self.selectors_close),
            (menu4,) + _MENU_SEPARATOR,
            (menuh,) + _MENU_SEPARATOR,
            (menuh, EventSpec.menu_help_widget, self.help_widget),
            (menuh,) + _MENU_SEPARATOR,
        ):
            if function is None:
                menu.add_separator()
                continue
            menu.add_command(
                label=accelerator[1],
                command=self.try_command(function, menu),
                underline=accelerator[3],
            )
        menu3.add_cascade(label="Time controls", menu=menu31, underline=0)
        menu3.add_separator()
        menu3.add_cascade(label="Playing modes", menu=menu32, underline=0)
        menu3.add_separator()

    def _initialize_database_interface(self):
        """Build tkinter notebook to display performance calculations."""

        # Notebook.
        notebook = tkinter.ttk.Notebook(master=self.widget)
        notebook.grid(column=0, row=0, sticky=tkinter.NSEW)
        self.widget.grid_rowconfigure(0, weight=1)
        self.widget.grid_columnconfigure(0, weight=1)

        # First tab: will be list of games referencing PGN file source.
        self._games_tab = tkinter.ttk.Frame(master=notebook)
        notebook.add(self._games_tab, text="Games", underline=0)
        self._games_tab.grid_rowconfigure(0, weight=1)
        self._games_tab.grid_columnconfigure(0, weight=1)
        self._games = games.Games(self._games_tab, self.database)
        self._games.frame.grid(column=0, row=0, sticky=tkinter.NSEW)

        # Second tab: will be list of unidentified players and list of
        # players with their identifiers, in two columns (unlike Results).
        self._players_tab = tkinter.ttk.Frame(master=notebook)
        notebook.add(self._players_tab, text="New players", underline=0)
        self._players_tab.grid_rowconfigure(0, weight=1)
        self._players_tab.grid_columnconfigure(0, weight=1)
        self._players = players.Players(self._players_tab, self.database)
        self._players.frame.grid(column=0, row=0, sticky=tkinter.NSEW)

        # Third tab: will be a list of players with their identifiers.
        self._persons_tab = tkinter.ttk.Frame(master=notebook)
        notebook.add(self._persons_tab, text="Identified players", underline=0)
        self._persons_tab.grid_rowconfigure(0, weight=1)
        self._persons_tab.grid_columnconfigure(0, weight=1)
        self._persons = persons.Persons(self._persons_tab, self.database)
        self._persons.frame.grid(column=0, row=0, sticky=tkinter.NSEW)

        # Fourth tab: will be a list of events.
        self._events_tab = tkinter.ttk.Frame(master=notebook)
        notebook.add(self._events_tab, text="Events", underline=0)
        self._events_tab.grid_rowconfigure(0, weight=1)
        self._events_tab.grid_columnconfigure(0, weight=1)
        self._events = events.Events(self._events_tab, self.database)
        self._events.frame.grid(column=0, row=0, sticky=tkinter.NSEW)

        # Fifth tab: will be a list of time controls.
        self._time_limits_tab = tkinter.ttk.Frame(master=notebook)
        notebook.add(self._time_limits_tab, text="Time controls", underline=0)
        self._time_limits_tab.grid_rowconfigure(0, weight=1)
        self._time_limits_tab.grid_columnconfigure(0, weight=1)
        self._time_limits = timecontrols.TimeControls(
            self._time_limits_tab, self.database
        )
        self._time_limits.frame.grid(column=0, row=0, sticky=tkinter.NSEW)

        # Sixth tab: will be a list of playing modes.
        self._modes_tab = tkinter.ttk.Frame(master=notebook)
        notebook.add(self._modes_tab, text="Modes", underline=0)
        self._modes_tab.grid_rowconfigure(0, weight=1)
        self._modes_tab.grid_columnconfigure(0, weight=1)
        self._modes = modes.Modes(self._modes_tab, self.database)
        self._modes.frame.grid(column=0, row=0, sticky=tkinter.NSEW)

        # Seventh tab: will be a list of performance calculation queries.
        self._calculations_tab = tkinter.ttk.Frame(master=notebook)
        notebook.add(self._calculations_tab, text="Calculations", underline=0)
        self._calculations_tab.grid_rowconfigure(0, weight=1)
        self._calculations_tab.grid_columnconfigure(0, weight=1)
        self._selectors = selectors.Selectors(
            self._calculations_tab, self.database
        )
        self._selectors.frame.grid(column=0, row=0, sticky=tkinter.NSEW)

        # Enable tab traversal.
        notebook.enable_traversal()

        # So it can be destoyed when closing database but not quitting.
        self._notebook = notebook

    def help_widget(self):
        """Display help in a Toplevel."""
        widget = tkinter.Toplevel(master=self.widget)
        rule_help = tkinter.Text(master=widget, wrap=tkinter.WORD)
        rule_help.grid_configure(column=0, row=0, sticky=tkinter.NSEW)
        widget.grid_columnconfigure(0, weight=1)
        widget.grid_rowconfigure(0, weight=1)
        rule_help.insert(tkinter.END, _HELP_TEXT)

    def database_quit(self):
        """Placeholder."""
        if not tkinter.messagebox.askyesno(
            parent=self.widget,
            message="Do you really want to quit?",
            title="Quit Chess Performance Calcultion",
        ):
            return
        self._database_quit()
        self.widget.winfo_toplevel().destroy()

    def database_verify(self):
        """Placeholder."""

    def database_close(self):
        """Close performance calculation database."""
        if self.database is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title="Close",
                message="No performance calculation database open",
            )
        elif self._database_class is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title="Close",
                message="Database interface not defined",
            )
        else:
            dlg = tkinter.messagebox.askquestion(
                parent=self.widget,
                title="Close",
                message="Close performance calculation database",
            )
            if dlg == tkinter.messagebox.YES:
                self._database_close()
                self.database = None
                self.set_error_file_name(None)
                # return False to inhibit context switch if invoked from close
                # Database button on tab because no state change is, or can be,
                # defined for that button.  The switch_context call above has
                # done what is needed.
                return False

    def database_delete(self):
        """Delete performance calculation database."""
        if self.database is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title="Delete",
                message="".join(
                    (
                        "Delete will not delete a database unless it can be ",
                        "opened.\n\nOpen the database and then Delete it.",
                    )
                ),
            )
            return
        dlg = tkinter.messagebox.askquestion(
            parent=self.widget,
            title="Delete",
            message="".join(
                (
                    "Please confirm that the performance calculation ",
                    "database in\n\n",
                    self.database.home_directory,
                    "\n\nis to be deleted.",
                )
            ),
        )
        if dlg == tkinter.messagebox.YES:

            # Replicate _database_close replacing close_database() call with
            # delete_database() call.  The close_database() call just before
            # setting database to None is removed.  The 'database is None'
            # test is done at start of this method.
            message = self.database.delete_database()
            if message:
                tkinter.messagebox.showinfo(
                    parent=self.widget, title="Delete", message=message
                )

            message = "".join(
                (
                    "The performance calculation database in\n\n",
                    self.database.home_directory,
                    "\n\nhas been deleted.",
                )
            )
            self.database = None
            self.set_error_file_name(None)
            tkinter.messagebox.showinfo(
                parent=self.widget, title="Delete", message=message
            )
        else:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title="Delete",
                message="".join(
                    (
                        "The performance calculation database ",
                        "has not been deleted",
                    )
                ),
            )

    def database_new(self):
        """Create and open a new performance calculation database."""
        if self.database is not None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                message="A performance calculation database is already open",
                title="New",
            )
            return

        conf = configuration.Configuration()
        database_folder = tkinter.filedialog.askdirectory(
            parent=self.widget,
            title="Select folder for new performance calculation database",
            initialdir=conf.get_configuration_value(constants.RECENT_DATABASE),
        )
        if not database_folder:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                message="".join(
                    (
                        "Create new performance calculation ",
                        "database cancelled",
                    )
                ),
                title="New",
            )
            return

        if os.path.exists(database_folder):
            modules = modulequery.modules_for_existing_databases(
                database_folder, filespec.FileSpec()
            )
            if modules is not None and len(modules):
                tkinter.messagebox.showinfo(
                    parent=self.widget,
                    message="".join(
                        (
                            "A performance calculation database ",
                            "already exists in ",
                            os.path.basename(database_folder),
                        )
                    ),
                    title="New",
                )
                return
        else:
            try:
                os.makedirs(database_folder)
            except OSError:
                tkinter.messagebox.showinfo(
                    parent=self.widget,
                    message="".join(
                        (
                            "Folder ",
                            os.path.basename(database_folder),
                            " already exists",
                        )
                    ),
                    title="New",
                )
                return
        conf.set_configuration_value(
            constants.RECENT_DATABASE,
            conf.convert_home_directory_to_tilde(database_folder),
        )

        # the default preference order is used rather than ask the user or
        # an order specific to this application.
        idm = modulequery.installed_database_modules()
        if len(idm) == 0:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                message="".join(
                    (
                        "No modules able to create database in\n\n",
                        os.path.basename(database_folder),
                        "\n\navailable.",
                    )
                ),
                title="New",
            )
            return
        _modulename = None
        _enginename = None
        for e in modulequery.DATABASE_MODULES_IN_DEFAULT_PREFERENCE_ORDER:
            if e in idm:
                if e in APPLICATION_DATABASE_MODULE:
                    _enginename = e
                    _modulename = APPLICATION_DATABASE_MODULE[e]
                    break
        if _modulename is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                message="".join(
                    (
                        "None of the available database engines can be ",
                        "used to ",
                        "create a database.",
                    )
                ),
                title="New",
            )
            return
        self._open_database_with_engine(
            database_folder, _modulename, _enginename, "New", "create"
        )
        if self.database:
            self._initialize_database_interface()

    def database_open(self):
        """Open performance calculation database."""
        if self.database is not None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                message="A performance calculation database is already open",
                title="Open",
            )
            return

        conf = configuration.Configuration()
        if self.database_folder is None:
            initdir = conf.get_configuration_value(constants.RECENT_DATABASE)
        else:
            initdir = self.database_folder
        database_folder = tkinter.filedialog.askdirectory(
            parent=self.widget,
            title="".join(
                (
                    "Select folder containing a performance ",
                    "calculation database",
                )
            ),
            initialdir=initdir,
            mustexist=tkinter.TRUE,
        )
        if not database_folder:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                message="Open performance calculation database cancelled",
                title="Open",
            )
            return
        conf.set_configuration_value(
            constants.RECENT_DATABASE,
            conf.convert_home_directory_to_tilde(database_folder),
        )

        ed = modulequery.modules_for_existing_databases(
            database_folder, filespec.FileSpec()
        )
        # A database module is chosen when creating the database
        # so there should be either only one entry in edt or None
        if not ed:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                message="".join(
                    (
                        "Folder ",
                        os.path.basename(database_folder),
                        " does not contain a performance calculation database",
                    )
                ),
                title="Open",
            )
            return
        elif len(ed) > 1:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                message="".join(
                    (
                        "There is more than one performance calculation ",
                        "database in folder\n\n",
                        os.path.basename(database_folder),
                        "\n\nMove the databases to separate folders and try ",
                        "again.  (Use the platform tools for moving files to ",
                        "relocate the database files.)",
                    )
                ),
                title="Open",
            )
            return

        idm = modulequery.installed_database_modules()
        _enginename = None
        for k, v in idm.items():
            if v in ed[0]:
                if _enginename:
                    tkinter.messagebox.showinfo(
                        parent=self.widget,
                        message="".join(
                            (
                                "Several modules able to open database in\n\n",
                                os.path.basename(database_folder),
                                "\n\navailable.  Unable to choose.",
                            )
                        ),
                        title="Open",
                    )
                    return
                _enginename = k
        if _enginename is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                message="".join(
                    (
                        "No modules able to open database in\n\n",
                        os.path.basename(database_folder),
                        "\n\navailable.",
                    )
                ),
                title="Open",
            )
            return
        _modulename = APPLICATION_DATABASE_MODULE[_enginename]
        self._open_database_with_engine(
            database_folder, _modulename, _enginename, "Open", "open"
        )
        if self.database:
            self._initialize_database_interface()

    def _open_database_with_engine(
        self, database_folder, _modulename, _enginename, title, action
    ):
        """Open performance calculation database with database engine."""
        if self._database_modulename != _modulename:
            if self._database_modulename is not None:
                tkinter.messagebox.showinfo(
                    parent=self.widget,
                    message="".join(
                        (
                            "The database engine needed for this database is ",
                            "not the one already in use.\n\nYou will have to ",
                            "Quit and start the application again to ",
                            action,
                            " this database.",
                        )
                    ),
                    title=title,
                )
                return
            self._database_enginename = _enginename
            self._database_modulename = _modulename

            def import_name(modulename, name):
                try:
                    module = __import__(
                        modulename, globals(), locals(), [name]
                    )
                except ImportError:
                    return None
                return getattr(module, name)

            self._database_class = import_name(_modulename, _Import.Database)

        try:
            self._database_open(database_folder)
        except KeyError as exc:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                message="".join(
                    (
                        "Unable to ",
                        action,
                        " database\n\n",
                        str(database_folder),
                        "\n\nThe reported reason is:\n\n",
                        str(exc),
                    )
                ),
                title=title,
            )
            self._database_close()
            self.database = None

    def _database_open(self, database_folder):
        """Open performance calculation database, creating it if necessary."""
        self.database = self._database_class(
            database_folder, **self._database_kargs
        )
        message = self.database.open_database()
        if message:
            tkinter.messagebox.showinfo(
                parent=self.widget, title="Open", message=message
            )
            return
        identity.create_player_identity_record_if_not_exists(self.database)
        identity.create_event_identity_record_if_not_exists(self.database)
        identity.create_time_limit_identity_record_if_not_exists(self.database)
        identity.create_playing_mode_identity_record_if_not_exists(
            self.database
        )
        self.database_folder = database_folder
        self.set_error_file_name(
            os.path.join(self.database_folder, ERROR_LOG)
        )

    def _database_close(self):
        """Close performance calculation database."""
        if self.database is None:
            return
        self.database.close_database()
        self._notebook.destroy()

    def _database_quit(self):
        """Quit performance calculation database."""
        if self.database is None:
            return
        self._database_close()
        self.database = None

    def database_import(self):
        """Import PGN headers to open database."""
        if self.database is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title="Import",
                message="".join(
                    (
                        "No performance calculation database open to ",
                        "receive import",
                    )
                ),
            )
            return
        if self._database_class is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title="Import",
                message="Database interface not defined",
            )
            return
        conf = configuration.Configuration()
        initdir = conf.get_configuration_value(constants.RECENT_PGN_DIRECTORY)
        pgn_directory = tkinter.filedialog.askdirectory(
            parent=self.widget,
            title="".join(
                (
                    "Select folder containing PGN files for import to ",
                    "the open performance calculation database",
                )
            ),
            initialdir=initdir,
            mustexist=tkinter.TRUE,
        )
        if not pgn_directory:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                message="Import to performance calculation database cancelled",
                title="Open",
            )
            return
        conf.set_configuration_value(
            constants.RECENT_PGN_DIRECTORY,
            conf.convert_home_directory_to_tilde(pgn_directory),
        )
        # gives time for destruction of dialogue and widget refresh
        # does nothing for obscuring and revealing application later
        self.widget.after_idle(
            self.try_command(self._import_pgnfiles, self.widget),
            pgn_directory,
        )

    def _import_pgnfiles(self, pgn_directory):
        """Import games to open database."""
        self.set_import_subprocess()  # raises exception if already active
        self._pgn_directory = pgn_directory
        self._games.games_grid.bind_off()
        self._players.players_grid.bind_off()
        self._players.persons_grid.bind_off()
        self._persons.data_grid.bind_off()
        self._selectors.selectors_grid.bind_off()
        self.database.close_database_contexts()
        self.set_import_subprocess(
            subprocess_id=multiprocessing.Process(
                target=rundu.rundu,
                args=(
                    self.database.home_directory,
                    pgn_directory,
                    self.database.use_deferred_update_process(),
                ),
            )
        )
        self.get_import_subprocess().start()
        self._import_pgnfiles_join()

    def set_import_subprocess(self, subprocess_id=None):
        """Set the import subprocess object if not already active."""
        if self.is_import_subprocess_active():
            raise CalculatorStartSubprocessError(
                "Attempt to set import subprocess while active"
            )
        self._import_subprocess = subprocess_id

    def get_import_subprocess(self):
        """Return the import subprocess identity."""
        return self._import_subprocess

    def is_import_subprocess_active(self):
        """Return True if the import subprocess object is active."""
        if self._import_subprocess is None:
            return False
        return self._import_subprocess.is_alive()

    def _import_pgnfiles_join(self):
        """After deferred_update process allow quit and reopen database."""
        if self.get_import_subprocess().exitcode is None:
            self.widget.after(1000, self._import_pgnfiles_join)
            return
        self.database.open_database()
        self._games.games_grid.bind_on()
        self._players.players_grid.bind_on()
        self._players.persons_grid.bind_on()
        self._persons.data_grid.bind_on()
        self._selectors.selectors_grid.bind_on()

    def player_identify(self):
        """Identify selected and bookmarked new players as selected person."""
        if self._players is None or self._players.frame is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_player_identify[1],
                message="Identify player as person not available at present",
            )
            return
        if self._players.players_grid is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_player_identify[1],
                message="List of new players not available at present",
            )
            return
        if self._players.persons_grid is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_player_identify[1],
                message="List of identified persons not available at present",
            )
            return
        if self._notebook.index(
            self._players_tab
        ) != self._notebook.index(self._notebook.select()):
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_player_identify[1],
                message="".join(
                    (
                        "List of new players is ",
                        "not the visible tab at present",
                    )
                ),
            )
            return
        self._players.identify()

    def player_break(self):
        """Break indentification of selected and bookmarked person aliases."""
        if self._persons is None or self._persons.frame is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_player_break[1],
                message="".join(
                    (
                        "Break selected person aliases ",
                        "not available at present",
                    )
                ),
            )
            return
        if self._persons.data_grid is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_player_break[1],
                message="List of identified persons not available at present",
            )
            return
        if self._notebook.index(
            self._persons_tab
        ) != self._notebook.index(self._notebook.select()):
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_player_break[1],
                message="".join(
                    (
                        "List of identified persons is ",
                        "not the visible tab at present",
                    )
                ),
            )
            return
        self._persons.break_selected()

    def player_split(self):
        """Split indentification of all aliases of selected person alias."""
        if self._persons is None or self._persons.frame is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_player_split[1],
                message="Split all person aliases not available at present",
            )
            return
        if self._persons.data_grid is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_player_split[1],
                message="List of identified persons not available at present",
            )
            return
        if self._notebook.index(
            self._persons_tab
        ) != self._notebook.index(self._notebook.select()):
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_player_split[1],
                message="".join(
                    (
                        "List of identified persons is ",
                        "not the visible tab at present",
                    )
                ),
            )
            return
        self._persons.split_all()

    def player_change(self):
        """Change person alias used as person identity."""
        if self._persons is None or self._persons.frame is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_player_split[1],
                message="Change person identity not available at present",
            )
            return
        if self._persons.data_grid is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_player_split[1],
                message="List of identified persons not available at present",
            )
            return
        if self._notebook.index(
            self._persons_tab
        ) != self._notebook.index(self._notebook.select()):
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_player_split[1],
                message="".join(
                    (
                        "List of identified persons is ",
                        "not the visible tab at present",
                    )
                ),
            )
            return
        self._persons.change_identity()

    def selectors_new(self):
        """Define new rule to select games for performance calculation."""

        # Is there a good reason to ban creating this type of tab if
        # no database is open?
        # At present the notebook does not exist unless a database is open.
        if not self._selectors_availbable(EventSpec.menu_selectors_new):
            return False

        # Do not prevent 'New Rule' based on current tab: maybe take some
        # default values based on selection in current tab.
        #if self._notebook.index(
        #    self._calculations_tab
        #) != self._notebook.index(self._notebook.select()):
        #    tkinter.messagebox.showinfo(
        #        parent=self.widget,
        #        title=EventSpec.menu_selectors_new[1],
        #        message="".join(
        #            (
        #                "List of game selection rules is ",
        #                "not the visible tab at present",
        #            )
        #        ),
        #    )
        #    return

        # A new 'New Rule' tab.
        rule_tab = tkinter.ttk.Frame(master=self._notebook)
        selector = rule.Rule(rule_tab, self.database)
        self._rule_tabs[
            rule_tab.winfo_pathname(rule_tab.winfo_id())
        ] = selector
        self._notebook.add(rule_tab, text="New Rule")

    def selectors_show(self):
        """Show selected rule to select games for performance calculation."""
        if not self._selectors_choose(EventSpec.menu_selectors_show):
            return

    def selectors_edit(self):
        """Edit selected rule to select games for performance calculation."""
        if not self._selectors_choose(EventSpec.menu_selectors_edit):
            return

    def _selectors_choose(self, menu_event_spec):
        """Return True if the selection rule list tab is visible."""
        if not self._selectors_availbable(menu_event_spec):
            return False
        if self._notebook.index(
            self._calculations_tab
        ) != self._notebook.index(self._notebook.select()):
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=menu_event_spec[1],
                message="".join(
                    (
                        "List of game selection rules is ",
                        "not the visible tab at present",
                    )
                ),
            )
            return False
        return True

    def _selectors_availbable(self, menu_event_spec):
        """Return True if the selection tabs are visible."""
        if self._selectors is None or self._selectors.frame is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=menu_event_spec[1],
                message="Define game selector rule not available at present",
            )
            return False
        if not self._selectors_grid_available(menu_event_spec):
            return False
        return True

    def selectors_close(self):
        """Close rule tab to select games for performance calculation."""
        if not self._selectors_apply(EventSpec.menu_selectors_close):
            return
        self._notebook.forget(tab)
        del self._rule_tabs[tab]

    def selectors_insert(self):
        """Insert rule to select games for performance calculation."""
        if not self._selectors_apply(EventSpec.menu_selectors_insert):
            return
        self._rule_tabs[tab].insert_rule()

    def selectors_update(self):
        """Update rule to select games for performance calculation."""
        if not self._selectors_apply(EventSpec.menu_selectors_update):
            return

    def selectors_delete(self):
        """Delete rule to select games for performance calculation."""
        if not self._selectors_apply(EventSpec.menu_selectors_delete):
            return

    def _selectors_apply(self, menu_event_spec):
        """Return True if a selection rule tab is visible."""
        if self._selectors is None or self._selectors.frame is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=menu_event_spec[1],
                message="Close game selector rule not available at present",
            )
            return False
        if not self._selectors_grid_available(menu_event_spec):
            return False
        tab = self._notebook.select()
        if tab not in self._rule_tabs:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=menu_event_spec[1],
                message="".join(
                    (
                        "A game selection rule is ",
                        "not the visible tab at present",
                    )
                ),
            )
            return False
        return True

    def _selectors_grid_available(self, menu_event_spec):
        """Return True if the selectors grid is visible."""
        if self._selectors.selectors_grid is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=menu_event_spec[1],
                message="List of game selection rules not available at present",
            )
            return False
        return True

    def event_identify(self):
        """Identify selected and bookmarked events as selected event."""
        if self._events is None or self._events.frame is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_event_identify[1],
                message="Identify event not available at present",
            )
            return
        if self._events.data_grid is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_event_identify[1],
                message="List of events not available at present",
            )
            return
        if self._notebook.index(
            self._events_tab
        ) != self._notebook.index(self._notebook.select()):
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_event_identify[1],
                message="".join(
                    (
                        "List of events is ",
                        "not the visible tab at present",
                    )
                ),
            )
            return
        self._events.identify()

    def event_break(self):
        """Break indentification of selected and bookmarked event aliases."""
        if self._events is None or self._events.frame is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_event_break[1],
                message="".join(
                    (
                        "Break event aliases ",
                        "not available at present",
                    )
                ),
            )
            return
        if self._events.data_grid is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_event_break[1],
                message="List of events not available at present",
            )
            return
        if self._notebook.index(
            self._events_tab
        ) != self._notebook.index(self._notebook.select()):
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_event_break[1],
                message="".join(
                    (
                        "List of events is ",
                        "not the visible tab at present",
                    )
                ),
            )
            return
        self._events.break_selected()

    def event_split(self):
        """Split indentification of all aliases of selected event alias."""
        if self._events is None or self._events.frame is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_event_split[1],
                message="Split all events not available at present",
            )
            return
        if self._events.data_grid is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_event_split[1],
                message="List of events not available at present",
            )
            return
        if self._notebook.index(
            self._events_tab
        ) != self._notebook.index(self._notebook.select()):
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_event_split[1],
                message="".join(
                    (
                        "List of events is ",
                        "not the visible tab at present",
                    )
                ),
            )
            return
        self._events.split_all()

    def event_change(self):
        """Change event alias used as event identity."""
        if self._events is None or self._events.frame is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_event_change[1],
                message="Change event identity not available at present",
            )
            return
        if self._events.data_grid is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_event_change[1],
                message="List of events not available at present",
            )
            return
        if self._notebook.index(
            self._events_tab
        ) != self._notebook.index(self._notebook.select()):
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_event_change[1],
                message="".join(
                    (
                        "List of events is ",
                        "not the visible tab at present",
                    )
                ),
            )
            return
        self._events.change_identity()

    def time_identify(self):
        """Identify bookmarked time controls as selected time control."""
        if self._time_limits is None or self._time_limits.frame is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_time_identify[1],
                message="Identify time control not available at present",
            )
            return
        if self._time_limits.data_grid is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_time_identify[1],
                message="List of time controls not available at present",
            )
            return
        if self._notebook.index(
            self._time_limits_tab
        ) != self._notebook.index(self._notebook.select()):
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_time_identify[1],
                message="".join(
                    (
                        "List of time controls is ",
                        "not the visible tab at present",
                    )
                ),
            )
            return
        self._time_limits.identify()

    def time_break(self):
        """Break indentity of selected and bookmarked time control aliases."""
        if self._time_limits is None or self._time_limits.frame is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_time_break[1],
                message="".join(
                    (
                        "Break time control aliases ",
                        "not available at present",
                    )
                ),
            )
            return
        if self._time_limits.data_grid is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_time_break[1],
                message="List of time controls not available at present",
            )
            return
        if self._notebook.index(
            self._time_limits_tab
        ) != self._notebook.index(self._notebook.select()):
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_time_break[1],
                message="".join(
                    (
                        "List of time controls is ",
                        "not the visible tab at present",
                    )
                ),
            )
            return
        self._time_limits.break_selected()

    def time_split(self):
        """Split identity of all aliases of selected time control."""
        if self._time_limits is None or self._time_limits.frame is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_time_split[1],
                message="Split all time controls not available at present",
            )
            return
        if self._time_limits.data_grid is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_time_split[1],
                message="List of time controls not available at present",
            )
            return
        if self._notebook.index(
            self._time_limits_tab
        ) != self._notebook.index(self._notebook.select()):
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_time_split[1],
                message="".join(
                    (
                        "List of time controls is ",
                        "not the visible tab at present",
                    )
                ),
            )
            return
        self._time_limits.split_all()

    def time_change(self):
        """Change time control alias used as time control identity."""
        if self._time_limits is None or self._time_limits.frame is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_time_change[1],
                message="Change time control identity not available at present",
            )
            return
        if self._time_limits.data_grid is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_time_change[1],
                message="List of time controls not available at present",
            )
            return
        if self._notebook.index(
            self._time_limits_tab
        ) != self._notebook.index(self._notebook.select()):
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_time_change[1],
                message="".join(
                    (
                        "List of time controls is ",
                        "not the visible tab at present",
                    )
                ),
            )
            return
        self._time_limits.change_identity()

    def mode_identify(self):
        """Identify bookmarked playing modes as selected playing mode."""
        if self._modes is None or self._modes.frame is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_mode_identify[1],
                message="Identify playing mode not available at present",
            )
            return
        if self._modes.data_grid is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_mode_identify[1],
                message="List of playing modes not available at present",
            )
            return
        if self._notebook.index(
            self._modes_tab
        ) != self._notebook.index(self._notebook.select()):
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_mode_identify[1],
                message="".join(
                    (
                        "List of playing modes is ",
                        "not the visible tab at present",
                    )
                ),
            )
            return
        self._modes.identify()

    def mode_break(self):
        """Break indentity of selected and bookmarked playing mode aliases."""
        if self._modes is None or self._modes.frame is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_mode_break[1],
                message="".join(
                    (
                        "Break playing mode aliases ",
                        "not available at present",
                    )
                ),
            )
            return
        if self._modes.data_grid is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_mode_break[1],
                message="List of playing modes not available at present",
            )
            return
        if self._notebook.index(
            self._modes_tab
        ) != self._notebook.index(self._notebook.select()):
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_mode_break[1],
                message="".join(
                    (
                        "List of playing modes is ",
                        "not the visible tab at present",
                    )
                ),
            )
            return
        self._modes.break_selected()

    def mode_split(self):
        """Split indentity of playing modes of selected playing mode alias."""
        if self._modes is None or self._modes.frame is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_mode_split[1],
                message="Split all playing modes not available at present",
            )
            return
        if self._modes.data_grid is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_mode_split[1],
                message="List of playing modes not available at present",
            )
            return
        if self._notebook.index(
            self._modes_tab
        ) != self._notebook.index(self._notebook.select()):
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_mode_split[1],
                message="".join(
                    (
                        "List of playing modes is ",
                        "not the visible tab at present",
                    )
                ),
            )
            return
        self._modes.split_all()

    def mode_change(self):
        """Change playing mode alias used as playing mode identity."""
        if self._modes is None or self._modes.frame is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_mode_change[1],
                message="Change playing mode identity not available at present",
            )
            return
        if self._modes.data_grid is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_mode_change[1],
                message="List of playing modes not available at present",
            )
            return
        if self._notebook.index(
            self._modes_tab
        ) != self._notebook.index(self._notebook.select()):
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_other_mode_change[1],
                message="".join(
                    (
                        "List of playing modes is ",
                        "not the visible tab at present",
                    )
                ),
            )
            return
        self._modes.change_identity()
