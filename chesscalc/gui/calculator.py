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

from solentware_misc.workarounds import workarounds

from .. import APPLICATION_NAME
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
from . import ruleedit
from . import ruleinsert
from . import ruleshow
from . import reportapply
from . import reportmirror
from ..core import identity
from ..core import tab_from_selection
from ..core import export
from ..core import apply_identities
from ..core import mirror_identities

ExceptionHandler.set_application_name(APPLICATION_NAME)

STARTUP_MINIMUM_WIDTH = 380
STARTUP_MINIMUM_HEIGHT = 400
_MENU_SEPARATOR = (None, None)

_HELP_TEXT = "".join(
    (
        "Performance calculations are based on either a particular ",
        "player or a list of events.\n\n",
        "Games are included only if they are associated with a player ",
        "entry listed on the 'Known players' tab.  This lists ",
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
        "on the 'Known players', 'Events', 'Time controls', and ",
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
        "with the identity on the 'Known players' tab must be the one ",
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
        "'Known players' tab.\n\n\n",
        "Event, time control, and playing mode entries can be identified ",
        "as references to the same thing by the relevant 'Identify ...' ",
        "action in the 'Other identities' menu.\n\n",
        "",
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
        self._report_tabs = {}
        self._games = None
        self._players = None
        self._persons = None
        self._events = None
        self._time_controls = None
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
        menu5 = tkinter.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Calculate", menu=menu5, underline=0)
        menu6 = tkinter.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Reports", menu=menu6, underline=0)
        menuh = tkinter.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Help", menu=menuh, underline=0)
        for menu, accelerator, function in (
            (menu1,) + _MENU_SEPARATOR,
            (menu1, EventSpec.menu_database_open, self._database_open),
            (menu1, EventSpec.menu_database_new, self._database_new),
            (menu1, EventSpec.menu_database_close, self._database_close),
            (menu1,) + _MENU_SEPARATOR,
            (menu1, EventSpec.menu_database_import, self._database_import),
            (
                menu1,
                EventSpec.menu_database_apply_aliases,
                self._database_apply_aliases,
            ),
            (
                menu1,
                EventSpec.menu_database_mirror_identities,
                self._database_mirror_identities,
            ),
            (menu1,) + _MENU_SEPARATOR,
            (
                menu1,
                EventSpec.menu_database_export_identities,
                self._database_export_identities,
            ),
            (menu1,) + _MENU_SEPARATOR,
            (menu1, EventSpec.menu_database_delete, self._database_delete),
            (menu1,) + _MENU_SEPARATOR,
            (menu1, EventSpec.menu_database_quit, self._database_quit),
            (menu1,) + _MENU_SEPARATOR,
            (menu2,) + _MENU_SEPARATOR,
            (menu2, EventSpec.menu_player_identify, self._player_identify),
            (menu2, EventSpec.menu_player_name_match, self._player_name_match),
            (menu2,) + _MENU_SEPARATOR,
            (menu2, EventSpec.menu_player_break, self._player_break),
            (menu2, EventSpec.menu_player_split, self._player_split),
            (menu2, EventSpec.menu_player_change, self._player_change),
            (menu2,) + _MENU_SEPARATOR,
            (menu2, EventSpec.menu_player_export, self._player_export),
            (menu2,) + _MENU_SEPARATOR,
            (menu3,) + _MENU_SEPARATOR,
            (menu3, EventSpec.menu_other_event_identify, self._event_identify),
            (menu3,) + _MENU_SEPARATOR,
            (menu3, EventSpec.menu_other_event_break, self._event_break),
            (menu3, EventSpec.menu_other_event_split, self._event_split),
            (menu3, EventSpec.menu_other_event_change, self._event_change),
            (menu3,) + _MENU_SEPARATOR,
            (
                menu3,
                EventSpec.menu_other_event_export_persons,
                self._event_export_persons,
            ),
            (menu3,) + _MENU_SEPARATOR,
            (menu31,) + _MENU_SEPARATOR,
            (menu31, EventSpec.menu_other_time_identify, self._time_identify),
            (menu31,) + _MENU_SEPARATOR,
            (menu31, EventSpec.menu_other_time_break, self._time_break),
            (menu31, EventSpec.menu_other_time_split, self._time_split),
            (menu31, EventSpec.menu_other_time_change, self._time_change),
            (menu31,) + _MENU_SEPARATOR,
            (menu32,) + _MENU_SEPARATOR,
            (menu32, EventSpec.menu_other_mode_identify, self._mode_identify),
            (menu32,) + _MENU_SEPARATOR,
            (menu32, EventSpec.menu_other_mode_break, self._mode_break),
            (menu32, EventSpec.menu_other_mode_split, self._mode_split),
            (menu32, EventSpec.menu_other_mode_change, self._mode_change),
            (menu32,) + _MENU_SEPARATOR,
            (menu4,) + _MENU_SEPARATOR,
            (menu4, EventSpec.menu_selectors_new, self._selectors_new),
            (menu4, EventSpec.menu_selectors_show, self._selectors_show),
            (menu4, EventSpec.menu_selectors_edit, self._selectors_edit),
            (menu4,) + _MENU_SEPARATOR,
            (menu4, EventSpec.menu_selectors_insert, self._selectors_insert),
            (menu4, EventSpec.menu_selectors_update, self._selectors_update),
            (menu4, EventSpec.menu_selectors_delete, self._selectors_delete),
            (menu4,) + _MENU_SEPARATOR,
            (menu4, EventSpec.menu_selectors_close, self._selectors_close),
            (menu4,) + _MENU_SEPARATOR,
            (menu5,) + _MENU_SEPARATOR,
            (menu5, EventSpec.menu_calculate_calculate, self._calculate),
            (menu5,) + _MENU_SEPARATOR,
            (menu5, EventSpec.menu_calculate_save, self._save),
            (menu5,) + _MENU_SEPARATOR,
            (menu6,) + _MENU_SEPARATOR,
            (menu6, EventSpec.menu_report_save, self._report_save),
            (menu6,) + _MENU_SEPARATOR,
            (menu6, EventSpec.menu_report_close, self._report_close),
            (menu6,) + _MENU_SEPARATOR,
            (menuh,) + _MENU_SEPARATOR,
            (menuh, EventSpec.menu_help_widget, self._help_widget),
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
        menu3.add_cascade(label="Modes", menu=menu32, underline=0)
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

        # Second tab: will be list of unidentified players and list of
        # players with their identifiers, in two columns (unlike Results).
        self._players_tab = tkinter.ttk.Frame(master=notebook)
        notebook.add(self._players_tab, text="New players", underline=0)
        self._players_tab.grid_rowconfigure(0, weight=1)
        self._players_tab.grid_columnconfigure(0, weight=1)
        self._players = players.Players(self._players_tab, self.database)

        # Third tab: will be a list of players with their identifiers.
        self._persons_tab = tkinter.ttk.Frame(master=notebook)
        notebook.add(self._persons_tab, text="Known players", underline=0)
        self._persons_tab.grid_rowconfigure(0, weight=1)
        self._persons_tab.grid_columnconfigure(0, weight=1)
        self._persons = persons.Persons(self._persons_tab, self.database)

        # Fourth tab: will be a list of events.
        self._events_tab = tkinter.ttk.Frame(master=notebook)
        notebook.add(self._events_tab, text="Events", underline=0)
        self._events_tab.grid_rowconfigure(0, weight=1)
        self._events_tab.grid_columnconfigure(0, weight=1)
        self._events = events.Events(self._events_tab, self.database)

        # Fifth tab: will be a list of time controls.
        self._time_limits_tab = tkinter.ttk.Frame(master=notebook)
        notebook.add(self._time_limits_tab, text="Time controls", underline=0)
        self._time_limits_tab.grid_rowconfigure(0, weight=1)
        self._time_limits_tab.grid_columnconfigure(0, weight=1)
        self._time_controls = timecontrols.TimeControls(
            self._time_limits_tab, self.database
        )

        # Sixth tab: will be a list of playing modes.
        self._modes_tab = tkinter.ttk.Frame(master=notebook)
        notebook.add(self._modes_tab, text="Modes", underline=0)
        self._modes_tab.grid_rowconfigure(0, weight=1)
        self._modes_tab.grid_columnconfigure(0, weight=1)
        self._modes = modes.Modes(self._modes_tab, self.database)

        # Seventh tab: will be a list of performance calculation queries.
        self._calculations_tab = tkinter.ttk.Frame(master=notebook)
        notebook.add(self._calculations_tab, text="Calculations", underline=0)
        self._calculations_tab.grid_rowconfigure(0, weight=1)
        self._calculations_tab.grid_columnconfigure(0, weight=1)
        self._selectors = selectors.Selectors(
            self._calculations_tab, self.database
        )

        # Enable tab traversal.
        notebook.enable_traversal()

        # So it can be destoyed when closing database but not quitting.
        self._notebook = notebook

    def _help_widget(self):
        """Display help in a Toplevel."""
        widget = tkinter.Toplevel(master=self.widget)
        rule_help = tkinter.Text(master=widget, wrap=tkinter.WORD)
        rule_help.grid_configure(column=0, row=0, sticky=tkinter.NSEW)
        widget.grid_columnconfigure(0, weight=1)
        widget.grid_rowconfigure(0, weight=1)
        rule_help.insert(tkinter.END, _HELP_TEXT)

    def _database_quit(self):
        """Quit performance calculation application."""
        if not tkinter.messagebox.askyesno(
            parent=self.widget,
            message="Do you really want to quit?",
            title="Quit Chess Performance Calcultion",
        ):
            return
        self._quit_database()
        self.widget.winfo_toplevel().destroy()

    def _database_apply_aliases(self):
        """Verify imported player identifications and apply if consistent."""
        title = EventSpec.menu_database_apply_aliases[1]
        if self.database is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=title,
                message="No performance calculation database open",
            )
            return None
        if self._database_class is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=title,
                message="Database interface not defined",
            )
            return None
        conf = configuration.Configuration()
        initdir = conf.get_configuration_value(
            constants.RECENT_IMPORT_DIRECTORY
        )
        import_file = tkinter.filedialog.askopenfilename(
            parent=self.widget,
            title=title,
            initialdir=initdir,
        )
        if not import_file:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                message="Import of person identifications cancelled",
                title=title,
            )
            return False
        conf.set_configuration_value(
            constants.RECENT_IMPORT_DIRECTORY,
            conf.convert_home_directory_to_tilde(os.path.dirname(import_file)),
        )
        # gives time for destruction of dialogue and widget refresh
        # does nothing for obscuring and revealing application later
        self.widget.after_idle(
            self.try_command(
                self._verify_and_apply_person_identities, self.widget
            ),
            import_file,
        )
        return True

    def _database_mirror_identities(self):
        """Verify imported player identifications and mirror if consistent."""
        title = EventSpec.menu_database_mirror_identities[1]
        if self.database is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=title,
                message="No performance calculation database open",
            )
            return None
        if self._database_class is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=title,
                message="Database interface not defined",
            )
            return None
        conf = configuration.Configuration()
        initdir = conf.get_configuration_value(
            constants.RECENT_IMPORT_DIRECTORY
        )
        import_file = tkinter.filedialog.askopenfilename(
            parent=self.widget,
            title=title,
            initialdir=initdir,
        )
        if not import_file:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                message="Import of mirror identifications cancelled",
                title=title,
            )
            return False
        conf.set_configuration_value(
            constants.RECENT_IMPORT_DIRECTORY,
            conf.convert_home_directory_to_tilde(os.path.dirname(import_file)),
        )
        # gives time for destruction of dialogue and widget refresh
        # does nothing for obscuring and revealing application later
        self.widget.after_idle(
            self.try_command(
                self._verify_and_mirror_person_identities, self.widget
            ),
            import_file,
        )
        return True

    def _database_export_identities(self):
        """Export player identifications."""
        title = EventSpec.menu_database_export_identities[1]
        if self.database is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=title,
                message="No performance calculation database open",
            )
            return None
        if self._database_class is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=title,
                message="Database interface not defined",
            )
            return None
        exporter = export.ExportIdentities(self.database)
        exporter.prepare_export_data()
        serialized_data = exporter.export_repr()
        conf = configuration.Configuration()
        initdir = conf.get_configuration_value(
            constants.RECENT_EXPORT_DIRECTORY
        )
        export_file = tkinter.filedialog.asksaveasfilename(
            parent=self.widget,
            title=title,
            initialdir=initdir,
            initialfile="mirror-identities.txt",
        )
        if not export_file:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                message="Export of mirror cancelled",
                title=title,
            )
            return False
        conf.set_configuration_value(
            constants.RECENT_EXPORT_DIRECTORY,
            conf.convert_home_directory_to_tilde(os.path.dirname(export_file)),
        )
        # gives time for destruction of dialogue and widget refresh
        # does nothing for obscuring and revealing application later
        # Why? the work is in the prepare_export_data() call earlier.
        # Might make sense if the exporter object were the argument.
        self.widget.after_idle(
            self.try_command(export.write_export_file, self.widget),
            export_file,
            serialized_data,
        )
        return True

    def _database_close(self):
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
                self._close_database()
                self.database = None
                self.set_error_file_name(None)
                # return False to inhibit context switch if invoked from close
                # Database button on tab because no state change is, or can be,
                # defined for that button.  The switch_context call above has
                # done what is needed.
                return False
        return None

    def _database_delete(self):
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
            self._notebook.destroy()
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

    def _database_new(self):
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
            if modules is not None and len(modules) > 0:
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
        for eng in modulequery.DATABASE_MODULES_IN_DEFAULT_PREFERENCE_ORDER:
            if eng in idm:
                if eng in APPLICATION_DATABASE_MODULE:
                    _enginename = eng
                    _modulename = APPLICATION_DATABASE_MODULE[eng]
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

    def _database_open(self):
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

        exdb = modulequery.modules_for_existing_databases(
            database_folder, filespec.FileSpec()
        )
        # A database module is chosen when creating the database
        # so there should be either only one entry in edt or None
        if not exdb:
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
        if len(exdb) > 1:
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
        for key, value in idm.items():
            if value in exdb[0]:
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
                _enginename = key
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
            self._open_database(database_folder)
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
            self._close_database()
            self.database = None

    def _open_database(self, database_folder):
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
        self.set_error_file_name(os.path.join(self.database_folder, ERROR_LOG))

    def _close_database(self):
        """Close performance calculation database."""
        if self.database is None:
            return
        self.database.close_database()
        self._notebook.destroy()

    def _quit_database(self):
        """Quit performance calculation database."""
        if self.database is None:
            return
        self._close_database()
        self.database = None

    def _database_import(self):
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
        self._set_import_subprocess()  # raises exception if already active
        self._pgn_directory = pgn_directory
        self._games.data_grid.bind_off()
        self._players.players_grid.bind_off()
        self._players.persons_grid.bind_off()
        self._persons.data_grid.bind_off()
        self._selectors.data_grid.bind_off()
        self.database.close_database_contexts()
        self._set_import_subprocess(
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

    def _set_import_subprocess(self, subprocess_id=None):
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
        self._games.data_grid.bind_on()
        self._players.players_grid.bind_on()
        self._players.persons_grid.bind_on()
        self._persons.data_grid.bind_on()
        self._selectors.data_grid.bind_on()
        self._games.data_grid.fill_view_with_top()

    def _is_player_tab_visible(self, title, prefix):
        """Return True if player tab is visible or False if not."""
        if self._players is None or self._players.frame is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=title,
                message=" ".join((prefix, "not available at present")),
            )
            return False
        if self._players.players_grid is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=title,
                message="List of new players not available at present",
            )
            return False
        if self._players.persons_grid is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=title,
                message="List of identified persons not available at present",
            )
            return False
        if self._notebook.index(self._players_tab) != self._notebook.index(
            self._notebook.select()
        ):
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=title,
                message="".join(
                    (
                        "List of new players is ",
                        "not the visible tab at present",
                    )
                ),
            )
            return False
        return True

    def _player_identify(self):
        """Identify selected and bookmarked new players as selected person."""
        if not self._is_player_tab_visible(
            EventSpec.menu_player_identify[1], "Identify player as person"
        ):
            return
        if self._players.identify():
            self._players.players_grid.clear_selections()
            self._players.players_grid.clear_bookmarks()
            self._players.persons_grid.clear_selections()
            self._players.players_grid.fill_view_with_top()
            self._players.persons_grid.fill_view_with_top()
            self._persons.data_grid.fill_view_with_top()

    def _player_name_match(self):
        """Identify selected and bookmarked new players as selected person."""
        if not self._is_player_tab_visible(
            EventSpec.menu_player_name_match[1], "Identify players by name"
        ):
            return
        if self._players.identify_by_name():
            self._players.players_grid.clear_selections()
            self._players.players_grid.clear_bookmarks()
            self._players.persons_grid.clear_selections()
            self._players.players_grid.fill_view_with_top()
            self._players.persons_grid.fill_view_with_top()
            self._persons.data_grid.fill_view_with_top()

    def _is_instance_tab_visible(self, instance, tab, name, title, prefix):
        """Return True if person tab is visible or False if not."""
        if instance is None or instance.frame is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=title,
                message=" ".join((prefix, "not available at present")),
            )
            return False
        if instance.data_grid is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=title,
                message=name.join(("List of ", " not available at present")),
            )
            return False
        if self._notebook.index(tab) != self._notebook.index(
            self._notebook.select()
        ):
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=title,
                message=name.join(
                    (
                        "List of ",
                        " is not the visible tab at present",
                    )
                ),
            )
            return False
        return True

    def _is_person_tab_visible(self, title, prefix):
        """Return True if person tab is visible or False if not."""
        return self._is_instance_tab_visible(
            self._persons,
            self._persons_tab,
            "identified persons",
            title,
            prefix,
        )

    def _player_break(self):
        """Break indentification of selected and bookmarked person aliases."""
        if not self._is_person_tab_visible(
            EventSpec.menu_player_break[1], "Break selected person aliases"
        ):
            return
        if self._persons.break_selected():
            self._players.persons_grid.clear_selections()
            self._players.persons_grid.clear_bookmarks()
            self._persons.data_grid.clear_selections()
            self._persons.data_grid.clear_bookmarks()
            self._players.players_grid.fill_view_with_top()
            self._players.persons_grid.fill_view_with_top()
            self._persons.data_grid.fill_view_with_top()

    def _player_split(self):
        """Split indentification of all aliases of selected person alias."""
        if not self._is_person_tab_visible(
            EventSpec.menu_player_split[1], "Split all person aliases"
        ):
            return
        if self._persons.split_all():
            self._players.persons_grid.clear_selections()
            self._players.persons_grid.clear_bookmarks()
            self._persons.data_grid.clear_selections()
            self._persons.data_grid.clear_bookmarks()
            self._players.players_grid.fill_view_with_top()
            self._players.persons_grid.fill_view_with_top()
            self._persons.data_grid.fill_view_with_top()

    def _player_change(self):
        """Change person alias used as person identity."""
        if not self._is_person_tab_visible(
            EventSpec.menu_player_change[1], "Change person identity"
        ):
            return
        if self._persons.change_identity():
            self._players.persons_grid.clear_selections()
            self._players.persons_grid.clear_bookmarks()
            self._persons.data_grid.clear_selections()
            self._persons.data_grid.clear_bookmarks()
            self._players.persons_grid.fill_view_with_top()
            self._persons.data_grid.fill_view_with_top()

    def _player_export(self):
        """Export aliases for known players in selection and bookmarks."""
        if not self._is_person_tab_visible(
            EventSpec.menu_player_export[1], "Export identified person"
        ):
            return
        if self._persons.export_selected_players():
            self._players.persons_grid.clear_selections()
            self._players.persons_grid.clear_bookmarks()
            self._persons.data_grid.clear_selections()
            self._persons.data_grid.clear_bookmarks()
            self._players.persons_grid.fill_view_with_top()
            self._persons.data_grid.fill_view_with_top()

    def _selectors_new(self):
        """Define new rule to select games for performance calculation."""
        if not self._selectors_availbable(EventSpec.menu_selectors_new):
            return
        persons_sel = self._persons.data_grid.selection
        events_sel = self._events.data_grid.selection
        events_bmk = self._events.data_grid.bookmarks
        time_controls_sel = self._time_controls.data_grid.selection
        modes_sel = self._modes.data_grid.selection
        frame = tkinter.ttk.Frame(master=self._notebook)
        tab = ruleinsert.RuleInsert(frame, self.database)
        try:
            tab_from_selection.get_person(tab, persons_sel, self.database)
        except rule.PopulatePerson as exc:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_selectors_new[1],
                message=str(exc),
            )
            return
        try:
            tab_from_selection.get_time_control(
                tab, time_controls_sel, self.database
            )
        except rule.PopulateTimeControl as exc:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_selectors_new[1],
                message=str(exc),
            )
            return
        try:
            tab_from_selection.get_mode(tab, modes_sel, self.database)
        except rule.PopulateMode as exc:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_selectors_new[1],
                message=str(exc),
            )
            return
        try:
            tab_from_selection.get_events(
                tab, events_sel, events_bmk, self.database
            )
        except rule.PopulateEvent as exc:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_selectors_new[1],
                message=str(exc),
            )
            return
        try:
            self._rule_tabs[frame.winfo_pathname(frame.winfo_id())] = tab
        except tkinter.TclError as exc:
            self._rule_tabs[workarounds.winfo_pathname(frame, exc)] = tab
        self._notebook.add(frame, text="New Rule")
        if persons_sel or self._persons.data_grid.bookmarks:
            self._persons.data_grid.clear_selections()
            self._persons.data_grid.clear_bookmarks()
            self._persons.data_grid.fill_view_with_top()
        if events_sel or events_bmk:
            self._events.data_grid.clear_selections()
            self._events.data_grid.clear_bookmarks()
            self._events.data_grid.fill_view_with_top()
        if time_controls_sel or self._time_controls.data_grid.bookmarks:
            self._time_controls.data_grid.clear_selections()
            self._time_controls.data_grid.clear_bookmarks()
            self._time_controls.data_grid.fill_view_with_top()
        if modes_sel or self._modes.data_grid.bookmarks:
            self._modes.data_grid.clear_selections()
            self._modes.data_grid.clear_bookmarks()
            self._modes.data_grid.fill_view_with_top()

    def _selectors_show(self):
        """Show selected rule to select games for performance calculation."""
        if not self._selectors_choose(EventSpec.menu_selectors_show):
            return
        selectors_sel = self._selectors.data_grid.selection
        if not selectors_sel:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_selectors_show[1],
                message="Please select a calculation rule",
            )
            return
        frame = tkinter.ttk.Frame(master=self._notebook)
        tab = ruleshow.RuleShow(frame, self.database)
        tab_from_selection.get_rule(tab, selectors_sel, self.database)
        try:
            self._rule_tabs[frame.winfo_pathname(frame.winfo_id())] = tab
        except tkinter.TclError as exc:
            self._rule_tabs[workarounds.winfo_pathname(frame, exc)] = tab
        self._notebook.add(frame, text="Show " + tab.get_rule_name_from_tab())
        self._selectors.data_grid.clear_selections()
        self._selectors.data_grid.clear_bookmarks()
        self._selectors.data_grid.fill_view_with_top()

    def _selectors_edit(self):
        """Edit selected rule to select games for performance calculation."""
        if not self._selectors_choose(EventSpec.menu_selectors_edit):
            return
        selectors_sel = self._selectors.data_grid.selection
        if not selectors_sel:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=EventSpec.menu_selectors_edit[1],
                message="Please select a calculation rule",
            )
            return
        frame = tkinter.ttk.Frame(master=self._notebook)
        tab = ruleedit.RuleEdit(frame, self.database)
        tab_from_selection.get_rule(tab, selectors_sel, self.database)
        try:
            self._rule_tabs[frame.winfo_pathname(frame.winfo_id())] = tab
        except tkinter.TclError as exc:
            self._rule_tabs[workarounds.winfo_pathname(frame, exc)] = tab
        self._notebook.add(frame, text="Edit " + tab.get_rule_name_from_tab())
        self._selectors.data_grid.clear_selections()
        self._selectors.data_grid.clear_bookmarks()
        self._selectors.data_grid.fill_view_with_top()

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

    def _selectors_close(self):
        """Close rule tab to select games for performance calculation."""
        tab = self._selectors_apply(EventSpec.menu_selectors_close)
        if not tab:
            return
        self._notebook.forget(tab)
        del self._rule_tabs[tab]

    def _selectors_insert(self):
        """Insert rule to select games for performance calculation."""
        tab = self._selectors_apply(EventSpec.menu_selectors_insert)
        if not tab:
            return
        if self._rule_tabs[tab].insert_rule():
            self._selectors.data_grid.clear_selections()
            self._selectors.data_grid.clear_bookmarks()
            self._selectors.data_grid.fill_view_with_top()

    def _selectors_update(self):
        """Update rule to select games for performance calculation."""
        tab = self._selectors_apply(EventSpec.menu_selectors_update)
        if not tab:
            return
        if self._rule_tabs[tab].update_rule():
            self._selectors.data_grid.clear_selections()
            self._selectors.data_grid.clear_bookmarks()
            self._selectors.data_grid.fill_view_with_top()

    def _selectors_delete(self):
        """Delete rule to select games for performance calculation."""
        tab = self._selectors_apply(EventSpec.menu_selectors_delete)
        if not tab:
            return
        if self._rule_tabs[tab].delete_rule():
            self._selectors.data_grid.clear_selections()
            self._selectors.data_grid.clear_bookmarks()
            self._selectors.data_grid.fill_view_with_top()

    def _selectors_apply(self, menu_event_spec):
        """Return tab if a selection rule tab is visible, False otherwise."""
        if self._selectors is None or self._selectors.frame is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=menu_event_spec[1],
                message="Game selector rule not available at present",
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
        return tab

    def _selectors_grid_available(self, menu_event_spec):
        """Return True if the selectors grid is visible."""
        if self._selectors.data_grid is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=menu_event_spec[1],
                message="".join(
                    ("List of game selection rules not available at present",)
                ),
            )
            return False
        return True

    def _is_event_tab_visible(self, title, prefix):
        """Return True if event tab is visible or False if not."""
        return self._is_instance_tab_visible(
            self._events, self._events_tab, "events", title, prefix
        )

    def _event_identify(self):
        """Identify selected and bookmarked events as selected event."""
        if not self._is_event_tab_visible(
            EventSpec.menu_other_event_identify[1], "Identify event"
        ):
            return
        if self._events.identify():
            self._events.data_grid.clear_selections()
            self._events.data_grid.clear_bookmarks()
            self._events.data_grid.fill_view_with_top()

    def _event_break(self):
        """Break indentification of selected and bookmarked event aliases."""
        if not self._is_event_tab_visible(
            EventSpec.menu_other_event_break[1], "Break event aliases"
        ):
            return
        if self._events.break_selected():
            self._events.data_grid.clear_selections()
            self._events.data_grid.clear_bookmarks()
            self._events.data_grid.fill_view_with_top()

    def _event_split(self):
        """Split indentification of all aliases of selected event alias."""
        if not self._is_event_tab_visible(
            EventSpec.menu_other_event_split[1], "Split all events"
        ):
            return
        if self._events.split_all():
            self._events.data_grid.clear_selections()
            self._events.data_grid.clear_bookmarks()
            self._events.data_grid.fill_view_with_top()

    def _event_change(self):
        """Change event alias used as event identity."""
        if not self._is_event_tab_visible(
            EventSpec.menu_other_event_change[1], "Change event identity"
        ):
            return
        if self._events.change_identity():
            self._events.data_grid.clear_selections()
            self._events.data_grid.clear_bookmarks()
            self._events.data_grid.fill_view_with_top()

    def _event_export_persons(self):
        """Export known players for events in selection and bookmarks.

        Aliases for the known players are included.

        """
        if not self._is_event_tab_visible(
            EventSpec.menu_other_event_export_persons[1],
            "Export event persons",
        ):
            return
        if self._events.export_players_in_selected_events():
            self._events.data_grid.clear_selections()
            self._events.data_grid.clear_bookmarks()
            self._events.data_grid.fill_view_with_top()

    def _is_time_tab_visible(self, title, prefix):
        """Return True if time control tab is visible or False if not."""
        return self._is_instance_tab_visible(
            self._time_controls,
            self._time_limits_tab,
            "time controls",
            title,
            prefix,
        )

    def _time_identify(self):
        """Identify bookmarked time controls as selected time control."""
        if not self._is_time_tab_visible(
            EventSpec.menu_other_time_identify[1], "Identify time control"
        ):
            return
        if self._time_controls.identify():
            self._time_controls.data_grid.clear_selections()
            self._time_controls.data_grid.clear_bookmarks()
            self._time_controls.data_grid.fill_view_with_top()

    def _time_break(self):
        """Break indentity of selected and bookmarked time control aliases."""
        if not self._is_time_tab_visible(
            EventSpec.menu_other_time_break[1], "Break time control aliases"
        ):
            return
        if self._time_controls.break_selected():
            self._time_controls.data_grid.clear_selections()
            self._time_controls.data_grid.clear_bookmarks()
            self._time_controls.data_grid.fill_view_with_top()

    def _time_split(self):
        """Split identity of all aliases of selected time control."""
        if not self._is_time_tab_visible(
            EventSpec.menu_other_time_split[1], "Split all time controls"
        ):
            return
        if self._time_controls.split_all():
            self._time_controls.data_grid.clear_selections()
            self._time_controls.data_grid.clear_bookmarks()
            self._time_controls.data_grid.fill_view_with_top()

    def _time_change(self):
        """Change time control alias used as time control identity."""
        if not self._is_time_tab_visible(
            EventSpec.menu_other_time_change[1], "Change time control identity"
        ):
            return
        if self._time_controls.change_identity():
            self._time_controls.data_grid.clear_selections()
            self._time_controls.data_grid.clear_bookmarks()
            self._time_controls.data_grid.fill_view_with_top()

    def _is_mode_tab_visible(self, title, prefix):
        """Return True if mode tab is visible or False if not."""
        return self._is_instance_tab_visible(
            self._modes, self._modes_tab, "playing modes", title, prefix
        )

    def _mode_identify(self):
        """Identify bookmarked playing modes as selected playing mode."""
        if not self._is_mode_tab_visible(
            EventSpec.menu_other_mode_identify[1], "Identify playing mode"
        ):
            return
        if self._modes.identify():
            self._modes.data_grid.clear_selections()
            self._modes.data_grid.clear_bookmarks()
            self._modes.data_grid.fill_view_with_top()

    def _mode_break(self):
        """Break indentity of selected and bookmarked playing mode aliases."""
        if not self._is_mode_tab_visible(
            EventSpec.menu_other_mode_break[1], "Break playing mode aliases"
        ):
            return
        if self._modes.break_selected():
            self._modes.data_grid.clear_selections()
            self._modes.data_grid.clear_bookmarks()
            self._modes.data_grid.fill_view_with_top()

    def _mode_split(self):
        """Split indentity of playing modes of selected playing mode alias."""
        if not self._is_mode_tab_visible(
            EventSpec.menu_other_mode_split[1], "Split all playing modes"
        ):
            return
        if self._modes.split_all():
            self._modes.data_grid.clear_selections()
            self._modes.data_grid.clear_bookmarks()
            self._modes.data_grid.fill_view_with_top()

    def _mode_change(self):
        """Change playing mode alias used as playing mode identity."""
        if not self._is_mode_tab_visible(
            EventSpec.menu_other_mode_change[1], "Change playing mode identity"
        ):
            return
        if self._modes.change_identity():
            self._modes.data_grid.clear_selections()
            self._modes.data_grid.clear_bookmarks()
            self._modes.data_grid.fill_view_with_top()

    def _calculate(self):
        """Calulate player performances from games selected by rule."""
        tab = self._selectors_apply(EventSpec.menu_calculate_calculate)
        if not tab:
            return
        self._rule_tabs[tab].calulate_performances_for_rule()
        return

    def _save(self):
        """Save calculted player performances from games selected by rule."""
        tab = self._selectors_apply(EventSpec.menu_calculate_save)
        if not tab:
            return
        tkinter.messagebox.showinfo(
            parent=self.widget,
            title=EventSpec.menu_calculate_save[1],
            message="Save not implemented yet",
        )
        return

    def _report_save(self):
        """Save report on apply identities."""
        tab = self._report_apply(EventSpec.menu_report_close)
        if not tab:
            return
        tkinter.messagebox.showinfo(
            parent=self.widget,
            title=EventSpec.menu_calculate_save[1],
            message="Save report not implemented yet",
        )
        return

    def _report_close(self):
        """Close report on apply identities."""
        tab = self._report_apply(EventSpec.menu_report_close)
        if not tab:
            return
        self._notebook.forget(tab)
        if tab in self._report_tabs:
            del self._report_tabs[tab]
        elif tab in self._rule_tabs:
            del self._rule_tabs[tab]

    def _report_apply(self, menu_event_spec):
        """Return tab if a selection rule tab is visible, False otherwise."""
        if self._notebook is None:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=menu_event_spec[1],
                message="Reports not available at present",
            )
            return False
        tab = self._notebook.select()
        if tab not in self._report_tabs and tab not in self._rule_tabs:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                title=menu_event_spec[1],
                message="".join(
                    (
                        "A report is ",
                        "not the visible tab at present",
                    )
                ),
            )
            return False
        return tab

    def _verify_and_apply_person_identities(self, import_file):
        """Verify imported player identifications and apply if consistent."""
        identities = export.read_export_file(import_file)
        report = apply_identities.verify_and_apply_identities(
            self.database, identities
        )
        frame = tkinter.ttk.Frame(master=self._notebook)
        tab = reportapply.ReportApply(frame, self.database)
        self._notebook.add(
            frame, text="Report " + os.path.basename(import_file)
        )
        try:
            self._report_tabs[frame.winfo_pathname(frame.winfo_id())] = tab
        except tkinter.TclError as exc:
            self._report_tabs[workarounds.winfo_pathname(frame, exc)] = tab
        tab.populate(report)
        if report.messages_exist:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                message="Identities not applied for reasons in report",
                title=EventSpec.menu_database_apply_aliases[1],
            )
            return

    def _verify_and_mirror_person_identities(self, import_file):
        """Verify imported player identifications and apply if consistent."""
        identities = export.read_export_file(import_file)
        report = mirror_identities.verify_and_mirror_identities(
            self.database, identities
        )
        frame = tkinter.ttk.Frame(master=self._notebook)
        tab = reportmirror.ReportMirror(frame, self.database)
        self._notebook.add(
            frame, text="Report " + os.path.basename(import_file)
        )
        try:
            self._report_tabs[frame.winfo_pathname(frame.winfo_id())] = tab
        except tkinter.TclError as exc:
            self._report_tabs[workarounds.winfo_pathname(frame, exc)] = tab
        tab.populate(report)
        if report.messages_exist:
            tkinter.messagebox.showinfo(
                parent=self.widget,
                message="Identities not mirrored for reasons in report",
                title=EventSpec.menu_database_mirror_identities[1],
            )
            return
