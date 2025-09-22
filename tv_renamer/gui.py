import tkinter as tk
from tkinter import font as tkFont
from tkinter import scrolledtext, ttk, messagebox


def show_error(title: str, error: str) -> None:
    messagebox.showerror(title, error)


# ------------------------------------------------------------------------------
# GUI HELPERS
def build_label_input(
    rootFrame: tk.Frame,
    inputLabel: str,
    row: int,
    textVariable: tk.StringVar,
    *,
    columnStart: int = 0,
    entryColumnSpan: int = 1,
    entryWidth: int = 10,
) -> None:
    """Construct a Tk Entry field with attached Label on given Frame. Will apply
    a initial grid setting given the applied grid row.

    Args:
        rootFrame (tk.Frame): Frame to attach widgets to
        inputLabel (str): Label in entry field
        row (int): Row index for grid layout
        textVariable (tk.StringVar): Text variable to bind to entry field
    """
    ttk.Label(rootFrame, text=inputLabel, width=20, padding=(2, 2), anchor=tk.E).grid(
        column=columnStart, row=row, sticky="E"
    )
    ttk.Entry(
        rootFrame, justify=tk.LEFT, textvariable=textVariable, width=entryWidth
    ).grid(column=(columnStart + 1), row=row, columnspan=entryColumnSpan, sticky="EW")


def event_toggle_state(widget: tk.Widget, state: int) -> None:
    """Toggle the state of a widget will need a widget that can be toggled
    between DISABLED and NORMAL.

    Widget also needs a "fg" as foreground color setting.

    State:
        0 - DISABLED
        1 - NORMAL

    Args:
        widget (tk.Widget): Widget for state toggle
        state (int): State variable
    """
    if state == 0:
        widget.config(state=tk.DISABLED, fg="lightgray")

    else:
        widget.config(state=tk.NORMAL, fg="red")


class AppGUI:
    """Application GUI class for renaming application"""

    # ROOT ELEMENTS
    __RootWin: tk.Tk
    __FontDefault: tkFont.Font
    __FontDefaultBold: tkFont.Font
    __FontDefaultSmall: tkFont.Font

    # SETTINGS VARIABLES
    __SettingMainDir: tk.StringVar
    __SettingShowDir: tk.StringVar
    __SettingShowName: tk.StringVar
    __SettingAppendix: tk.StringVar
    __SettingFiletype: tk.StringVar
    __SettingSeparator: tk.StringVar
    __SettingEpisodeRegex: tk.StringVar
    __SettingSeasonRegex: tk.StringVar
    __SettingSpecialVerRegex: tk.StringVar

    # BUTTONS
    __ButtonScan: tk.Button
    __ButtonLaunch: tk.Button

    # OUTPUT FIELDS
    __FieldInput: scrolledtext.ScrolledText
    __FieldOutput: scrolledtext.ScrolledText

    # --------------------------------------------------------------------------
    # INIT
    def __init__(self) -> None:
        """Initialize the application GUI"""
        # init root window
        self.__build_root()

        # build variables
        # STRING ENTRIES
        self.__SettingShowDir = tk.StringVar()
        self.__SettingShowName = tk.StringVar()
        self.__SettingAppendix = tk.StringVar()
        self.__SettingFiletype = tk.StringVar()
        self.__SettingSeparator = tk.StringVar()

        self.__SettingEpisodeRegex = tk.StringVar()
        self.__SettingEpisodePosition = tk.StringVar()
        self.__SettingEpisodeOffset = tk.StringVar()

        self.__SettingSeasonRegex = tk.StringVar()
        self.__SettingSeasonPosition = tk.StringVar()
        self.__SettingSeasonOffset = tk.StringVar()

        self.__SettingSpecialVerRegex = tk.StringVar()
        self.__SettingSpecialVerPosition = tk.StringVar()
        self.__SettingSpecialVerOffset = tk.StringVar()
        # FONTS
        self.__FontDefault = tkFont.nametofont("TkDefaultFont")
        self.__FontDefaultBold = self.__FontDefault.copy()
        self.__FontDefaultBold.config(weight="bold")
        self.__FontDefaultSmall = self.__FontDefault.copy()
        self.__FontDefaultSmall.config(size=9)

        # construct GUI
        self.__init_gui()

    # --------------------------------------------------------------------------
    # GUI CONSTRUCTION
    def __build_root(self) -> None:
        """Construct the main GUI elements"""
        self.__RootWin = tk.Tk()
        self.__RootWin.minsize(740, 520)
        self.__RootWin.resizable(width=False, height=False)
        self.__RootWin.title("TV Show Renamer")

    def __init_gui(self) -> None:
        # MAIN FRAME
        FrameBase = ttk.Frame(self.__RootWin)
        FrameBase.grid()

        # INPUT SECTION
        ttk.Label(
            FrameBase, text="Inputs", padding=(2, 2), font=self.__FontDefaultBold
        ).grid(column=1, row=0, columnspan=3)

        build_label_input(
            FrameBase, "Show Directory", 1, self.__SettingShowDir, entryColumnSpan=5
        )
        build_label_input(
            FrameBase, "Show Name", 2, self.__SettingShowName, entryColumnSpan=5
        )
        build_label_input(
            FrameBase, "Appendix", 3, self.__SettingAppendix, entryColumnSpan=5
        )
        build_label_input(
            FrameBase, "File Type", 4, self.__SettingFiletype, entryColumnSpan=5
        )
        build_label_input(
            FrameBase, "Separator", 5, self.__SettingSeparator, entryColumnSpan=5
        )

        build_label_input(
            FrameBase, "Episode Regex", 6, self.__SettingEpisodeRegex, entryWidth=20
        )
        build_label_input(
            FrameBase,
            "Episode Offset",
            6,
            self.__SettingEpisodeOffset,
            columnStart=2,
            entryWidth=10,
        )
        build_label_input(
            FrameBase,
            "Episode Position",
            6,
            self.__SettingEpisodePosition,
            columnStart=4,
            entryWidth=10,
        )

        build_label_input(
            FrameBase, "Season Regex", 7, self.__SettingSeasonRegex, entryWidth=20
        )
        build_label_input(
            FrameBase,
            "Season Offset",
            7,
            self.__SettingSeasonOffset,
            columnStart=2,
            entryWidth=10,
        )
        build_label_input(
            FrameBase,
            "Season Position",
            7,
            self.__SettingSeasonPosition,
            columnStart=4,
            entryWidth=10,
        )

        build_label_input(
            FrameBase, "Version Regex", 8, self.__SettingSpecialVerRegex, entryWidth=20
        )
        build_label_input(
            FrameBase,
            "Version Offset",
            8,
            self.__SettingSpecialVerOffset,
            columnStart=2,
            entryWidth=10,
        )
        build_label_input(
            FrameBase,
            "Version Position",
            8,
            self.__SettingSpecialVerPosition,
            columnStart=4,
            entryWidth=10,
        )

        RowIdx = 9
        # CONFIRM BUTTONS
        self.__ButtonLaunch = tk.Button(
            FrameBase,
            text="GO!",
            state=tk.DISABLED,
            fg="lightgray",
            font=self.__FontDefaultBold,
        )
        self.__ButtonLaunch.grid(
            column=1, row=RowIdx, padx=2, pady=2, sticky="EW", columnspan=2
        )
        self.__ButtonScan = tk.Button(FrameBase, text="Scan")
        self.__ButtonScan.grid(
            column=3, row=RowIdx, padx=2, pady=2, sticky="EW", columnspan=3
        )

        StateEnabled = tk.IntVar()
        StateEnabled.trace_add(
            "write",
            lambda var, index, mode: event_toggle_state(  # noqa: ARG005
                self.__ButtonLaunch, StateEnabled.get()
            ),
        )
        ttk.Checkbutton(FrameBase, text="Enable Write", variable=StateEnabled).grid(
            column=0, row=RowIdx
        )

        # ---
        RowIdx += 1
        ttk.Separator(FrameBase, orient=tk.HORIZONTAL, style="").grid(
            column=0, row=RowIdx, columnspan=6, sticky="EW", padx=2, pady=2
        )

        # ---
        # OUTPUT FIELDS
        RowIdx += 1
        ttk.Label(FrameBase, text="Input Files", padding=(2, 2)).grid(
            column=0, row=RowIdx, columnspan=3
        )
        ttk.Label(FrameBase, text="Output Files", padding=(2, 2)).grid(
            column=3, row=RowIdx, columnspan=3
        )
        # ---
        RowIdx += 1
        self.__FieldInput = scrolledtext.ScrolledText(
            FrameBase, width=60, height=15, font=self.__FontDefaultSmall, fg="gray"
        )
        self.__FieldInput.grid(column=0, row=RowIdx, columnspan=3, padx=2, pady=2)
        self.__FieldInput.insert("1.0", "Input Files...")
        self.__FieldInput.config(state=tk.DISABLED)
        # -
        self.__FieldOutput = scrolledtext.ScrolledText(
            FrameBase, width=60, height=15, font=self.__FontDefaultSmall, fg="gray"
        )
        self.__FieldOutput.grid(column=3, row=RowIdx, columnspan=3, padx=2, pady=2)
        self.__FieldOutput.insert("1.0", "Output Files...")
        self.__FieldOutput.config(state=tk.DISABLED)

    # --------------------------------------------------------------------------
    # DATA VARIABLES
    @property
    def ShowDir(self) -> str:
        return self.__SettingShowDir.get()

    @ShowDir.setter
    def ShowDir(self, value: str) -> None:
        self.__SettingShowDir.set(value)

    # ---
    @property
    def ShowName(self) -> str:
        return self.__SettingShowName.get()

    @ShowName.setter
    def ShowName(self, value: str) -> None:
        self.__SettingShowName.set(value)

    # ---
    @property
    def Appendix(self) -> str:
        return self.__SettingAppendix.get()

    @Appendix.setter
    def Appendix(self, value: str) -> None:
        self.__SettingAppendix.set(value)

    # ---
    @property
    def Filetype(self) -> str:
        return self.__SettingFiletype.get()

    @Filetype.setter
    def Filetype(self, value: str) -> None:
        self.__SettingFiletype.set(value)

    # ---
    @property
    def Separator(self) -> str:
        return self.__SettingSeparator.get()

    @Separator.setter
    def Separator(self, value: str) -> None:
        self.__SettingSeparator.set(value)

    # ---
    @property
    def EpisodeRegex(self) -> str:
        return self.__SettingEpisodeRegex.get()

    @EpisodeRegex.setter
    def EpisodeRegex(self, value: str) -> None:
        self.__SettingEpisodeRegex.set(value)

    # ---
    @property
    def EpisodeOffset(self) -> str:
        return self.__SettingEpisodeOffset.get()

    @EpisodeOffset.setter
    def EpisodeOffset(self, value: str) -> None:
        self.__SettingEpisodeOffset.set(value)

    # ---
    @property
    def EpisodePosition(self) -> str:
        return self.__SettingEpisodePosition.get()

    @EpisodePosition.setter
    def EpisodePosition(self, value: str) -> None:
        self.__SettingEpisodePosition.set(value)

    # ---
    @property
    def SeasonRegex(self) -> str:
        return self.__SettingSeasonRegex.get()

    @SeasonRegex.setter
    def SeasonRegex(self, value: str) -> None:
        self.__SettingSeasonRegex.set(value)

    # ---
    @property
    def SeasonOffset(self) -> str:
        return self.__SettingSeasonOffset.get()

    @SeasonOffset.setter
    def SeasonOffset(self, value: str) -> None:
        self.__SettingSeasonOffset.set(value)

    # ---
    @property
    def SeasonPosition(self) -> str:
        return self.__SettingSeasonPosition.get()

    @SeasonPosition.setter
    def SeasonPosition(self, value: str) -> None:
        self.__SettingSeasonPosition.set(value)

    # ---
    @property
    def SpecialVerRegex(self) -> str:
        return self.__SettingSpecialVerRegex.get()

    @SpecialVerRegex.setter
    def SpecialVerRegex(self, value: str) -> None:
        self.__SettingSpecialVerRegex.set(value)

    # ---
    @property
    def SpecialVerOffset(self) -> str:
        return self.__SettingSpecialVerOffset.get()

    @SpecialVerOffset.setter
    def SpecialVerOffset(self, value: str) -> None:
        self.__SettingSpecialVerOffset.set(value)

    # ---
    @property
    def SpecialVerPosition(self) -> str:
        return self.__SettingSpecialVerPosition.get()

    @SpecialVerPosition.setter
    def SpecialVerPosition(self, value: str) -> None:
        self.__SettingSpecialVerPosition.set(value)

    # ---
    @property
    def InputFilesField(self) -> str:
        return self.__FieldInput

    @InputFilesField.setter
    def InputFilesField(self, value: str) -> None:
        self.__FieldInput.config(state=tk.NORMAL)
        self.__FieldInput.delete("1.0", tk.END)
        self.__FieldInput.insert("1.0", value)
        self.__FieldInput.config(state=tk.DISABLED)

    # ---
    @property
    def OutputFilesField(self) -> str:
        return self.__FieldOutput

    @OutputFilesField.setter
    def OutputFilesField(self, value: str) -> None:
        self.__FieldOutput.config(state=tk.NORMAL)
        self.__FieldOutput.delete("1.0", tk.END)
        self.__FieldOutput.insert("1.0", value)
        self.__FieldOutput.config(state=tk.DISABLED)

    # --------------------------------------------------------------------------
    # MAINLOOP
    def run(self) -> None:
        """Render GUI with application loop"""
        return self.__RootWin.mainloop()

    # --------------------------------------------------------------------------
    # CALLBACKS
    def register_callback_scan(self, action) -> None:  # noqa: ANN001
        self.__ButtonScan.config(command=action)

    def register_callback_launch(self, action) -> None:  # noqa: ANN001
        self.__ButtonLaunch.config(command=action)
