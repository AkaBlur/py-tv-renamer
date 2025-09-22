from __future__ import annotations
import gui
from pathlib import Path
import re
import shutil

import renamer
import settings
import util


class RenamerApp:
    """Main application class for renaming app."""

    __MainGUI: gui.AppGUI
    __ParseSettings: settings.BatchSettings
    __WorkDir: Path = None
    __ConfigFile: Path = None

    # --------------------------------------------------------------------------
    # INITIALIZATION
    def __init__(self, workDirectory: Path | None = None) -> None:
        """Initialize application and settings.

        Optionally overwrites the default show directory to the current working
        directory

        Args:
            workDirectory (Path | None, optional):
                Optional working directory as TV show directory.
                Defaults to None.
        """
        self.__MainGUI = gui.AppGUI()
        self.__ParseSettings = settings.BatchSettings()

        if workDirectory is not None:
            self.__WorkDir = workDirectory

    def register_callbacks(self) -> None:
        self.__MainGUI.register_callback_launch(self.run_renamer)
        self.__MainGUI.register_callback_scan(self.run_scan)

    # --------------------------------------------------------------------------
    # RUNNER
    def run(self) -> None:
        """Run app loop"""
        self.__MainGUI.run()

    def shutdown(self) -> None:
        """App shutdown procedures"""
        self.__ParseSettings.ShowDir = Path(self.__MainGUI.ShowDir)
        self.__ParseSettings.ShowName = self.__MainGUI.ShowName
        self.__ParseSettings.Appendix = self.__MainGUI.Appendix
        self.__ParseSettings.FileExtension = self.__MainGUI.Filetype
        self.__ParseSettings.SepStr = self.__MainGUI.Separator

        self.__ParseSettings.EpisodeRegex = self.__MainGUI.EpisodeRegex
        self.__ParseSettings.EpisodeOffset = util.safe_convert_int(
            self.__MainGUI.EpisodeOffset
        )
        self.__ParseSettings.EpisodePosition = util.safe_convert_int(
            self.__MainGUI.EpisodePosition
        )

        self.__ParseSettings.SeasonRegex = self.__MainGUI.SeasonRegex
        self.__ParseSettings.SeasonOffset = util.safe_convert_int(
            self.__MainGUI.SeasonOffset
        )
        self.__ParseSettings.SeasonPosition = util.safe_convert_int(
            self.__MainGUI.SeasonPosition
        )

        self.__ParseSettings.SpecialVerRegex = self.__MainGUI.SpecialVerRegex
        self.__ParseSettings.SpecialVerOffset = util.safe_convert_int(
            self.__MainGUI.SpecialVerOffset
        )
        self.__ParseSettings.SpecialVerPosition = util.safe_convert_int(
            self.__MainGUI.SpecialVerPosition
        )

        self.__ParseSettings.save_settings(self.__ConfigFile)

    # --------------------------------------------------------------------------
    # SETTINGS
    def load_settings(self, jsonConfig: Path | None = None) -> None:
        """Load application settings.

        By default takes the supplied configuration file for dynamic setting
        storage.

        Args:
            jsonConfig (Path | None, optional):
                JSON config file. Defaults to None.
        """
        if jsonConfig is not None:
            self.__ConfigFile = jsonConfig

        else:
            self.__ConfigFile = Path(__file__).parent / "config.json"

        # check for config file
        if util.check_file(self.__ConfigFile) != util.PathError.CORRECT:
            shutil.copy(
                (Path(__file__).parent / "default.json"),
                (Path(__file__).parent / "config.json"),
            )

        self.__ParseSettings.load_settings(self.__ConfigFile)

        # overwrite default show directory to given work directory
        if self.__WorkDir is not None:
            self.__ParseSettings.ShowDir = self.__WorkDir

        self.__MainGUI.ShowDir = str(self.__ParseSettings.ShowDir)
        self.__MainGUI.ShowName = self.__ParseSettings.ShowName
        self.__MainGUI.Appendix = self.__ParseSettings.Appendix
        self.__MainGUI.Filetype = self.__ParseSettings.FileExtension
        self.__MainGUI.Separator = self.__ParseSettings.SepStr

        self.__MainGUI.EpisodeRegex = self.__ParseSettings.EpisodeRegex
        self.__MainGUI.EpisodeOffset = self.__ParseSettings.EpisodeOffset
        self.__MainGUI.EpisodePosition = self.__ParseSettings.EpisodePosition

        self.__MainGUI.SeasonRegex = self.__ParseSettings.SeasonRegex
        self.__MainGUI.SeasonOffset = self.__ParseSettings.SeasonOffset
        self.__MainGUI.SeasonPosition = self.__ParseSettings.SeasonPosition

        self.__MainGUI.SpecialVerRegex = self.__ParseSettings.SpecialVerRegex
        self.__MainGUI.SpecialVerOffset = self.__ParseSettings.SpecialVerOffset
        self.__MainGUI.SpecialVerPosition = self.__ParseSettings.SpecialVerPosition

    def __check_regex(self, regType: str) -> bool:
        if regType not in ["Episode", "Season", "SpecialVer"]:
            Err = "Undefined Regex variable to check!"
            raise RuntimeError(Err)

        MemberRegVar = getattr(self.__MainGUI, f"{regType}Regex").strip()

        # length
        if len(MemberRegVar) == 0 or MemberRegVar == "":
            gui.show_error("Settings Error", f"{regType} regex cannot be empty!")
            return False

        # capture group
        if MemberRegVar.count("(") != 1 or MemberRegVar.count(")") != 1:
            gui.show_error(
                "Setting Error", f"{regType} must feature exactly one capture group!"
            )
            return False

        # valid regular expression
        try:
            re.compile(MemberRegVar)

        except re.error as e:
            gui.show_error("Settings Error", f"{regType} Regex incorrect - {e}")
            return False

        setattr(self.__ParseSettings, f"{regType}Regex", MemberRegVar)
        return True

    def validate_settings(self) -> bool:
        """Validate main settings from GUI for application

        Returns:
            bool: True if correct, False otherwise
        """
        # SHOW DIRECTORY
        ShowDirCheck = util.check_dir(Path(self.__MainGUI.ShowDir))

        if ShowDirCheck == util.PathError.NOT_EXISTING:
            gui.show_error("Settings Error", "Show Directory not found!")
            return False

        if ShowDirCheck == util.PathError.WRONG_TYPE:
            gui.show_error("Settings Error", "Show Directory not a folder!")
            return False

        self.__ParseSettings.ShowDir = Path(self.__MainGUI.ShowDir)

        # SHOW NAME
        if len(self.__MainGUI.ShowName) == 0 or self.__MainGUI.ShowName == "":
            gui.show_error("Settings Error", "Show Name can't be empty!")
            return False

        self.__ParseSettings.ShowName = self.__MainGUI.ShowName

        # APPENDIX
        self.__ParseSettings.Appendix = self.__MainGUI.Appendix

        # FILETYPE
        if len(self.__MainGUI.Filetype) == 0 or self.__MainGUI.Filetype == "":
            gui.show_error("Settings Error", "File Extension can't be empty!")
            return False

        self.__ParseSettings.FileExtension = self.__MainGUI.Filetype

        # SEPARATOR
        if len(self.__MainGUI.Separator) == 0 or self.__MainGUI.Separator == "":
            gui.show_error("Settings Error", "Separator can't be empty!")
            return False

        if len(self.__MainGUI.Separator) != 1:
            gui.show_error("Settings Error", "Separator must be single character!")
            return False

        self.__ParseSettings.SepStr = self.__MainGUI.Separator

        # EPISODE
        if not self.__check_regex("Episode"):
            return False

        self.__ParseSettings.EpisodeOffset = util.safe_convert_int(
            self.__MainGUI.EpisodeOffset
        )
        self.__ParseSettings.EpisodePosition = util.safe_convert_int(
            self.__MainGUI.EpisodePosition
        )

        # SEASON
        if not self.__check_regex("Season"):
            return False

        self.__ParseSettings.SeasonOffset = util.safe_convert_int(
            self.__MainGUI.SeasonOffset
        )
        self.__ParseSettings.SeasonPosition = util.safe_convert_int(
            self.__MainGUI.SeasonPosition
        )

        # SPECIAL VERSION
        if not self.__check_regex("SpecialVer"):
            return False

        self.__ParseSettings.SpecialVerOffset = util.safe_convert_int(
            self.__MainGUI.SpecialVerOffset
        )
        self.__ParseSettings.SpecialVerPosition = util.safe_convert_int(
            self.__MainGUI.SpecialVerPosition
        )

        return True

    # --------------------------------------------------------------------------
    # ACTIONS
    def run_scan(self) -> list[renamer.SeasonEpisodeResult]:
        """Run a scan for all files detectable with given settings. Already
        construct a new filename for every correctly detected file.

        Returns:
            list[renamer.SeasonEpisodeResult]: List of scan results
        """
        if not self.validate_settings():
            # GUI already registers error messages to user
            return []

        # get extraction info
        ExtractedFileInfos = renamer.list_season_episode(self.__ParseSettings)
        # GUI output
        ScanInputStr = ""
        ScanOutputStr = ""

        for Info in ExtractedFileInfos:
            if Info.ResultState != renamer.RenamerError.NO_ERROR:
                ErrMsg = f"{renamer.get_error_representation(Info.ResultState)}\n{Info.CurrentName}"  # noqa: E501
                gui.show_error("Extract Error", ErrMsg)
                return []

            ScanInputStr += f"\nFound: {Info.CurrentName}"
            ScanInputStr += (
                f"\n\tE: {Info.Episode}\tS: {Info.Season}\tV: {Info.SpecialVer}"
            )
            ScanOutputStr += f"\n{Info.ReformattedName}"

        ScanInputStr = ScanInputStr.strip("\n")
        self.__MainGUI.InputFilesField = ScanInputStr

        ScanOutputStr = ScanOutputStr.strip("\n")
        self.__MainGUI.OutputFilesField = ScanOutputStr

        return ExtractedFileInfos

    def run_renamer(self) -> None:
        """Run renamer on files found via input settings."""
        # scanner also validates settings first
        ScanResult = self.run_scan()

        if len(ScanResult) == 0:
            return

        renamer.rename_files(self.__ParseSettings, ScanResult)
