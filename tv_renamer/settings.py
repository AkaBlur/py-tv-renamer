import dataclasses
import json
from pathlib import Path


@dataclasses.dataclass
class BatchSettings:
    ShowDir: Path = dataclasses.field(default_factory=lambda: Path())
    """Directory for given TV series"""
    ShowName: str = ""
    """Name of given TV series"""
    FileExtension: str = ""
    """Extension of files for TV series"""
    SepStr: str = ""
    """Separator for individual components in filename"""

    Appendix: str = ""
    """Appendix for TV show naming"""

    EpisodeRegex: str = ""
    """Regex to find episode number"""
    EpisodePosition: int = 0
    """Position of episode part in filename"""
    EpisodeOffset: int = 0
    """Numeric offset for episode number"""
    EpisodeLargest: int = 99
    """Largest episode number to encounter"""

    SeasonRegex: str = ""
    """Regex to find season number"""
    SeasonPosition: int = 0
    """Position of season part in filename"""
    SeasonOffset: int = 0
    """Numeric offset for season number"""

    SpecialVerRegex: str = ""
    """Regex to find special version number"""
    SpecialVerPosition: int = 0
    """Position of special version part in filename"""
    SpecialVerOffset: int = 0
    """Numeric offset for special version number"""

    def load_settings(self, jsonFile: Path) -> None:
        """Load configuration settings from a given file.

        Args:
            jsonFile (Path): Config JSON file

        Raises:
            RuntimeError: JSON file with wrong format
        """
        if not jsonFile.exists() or not jsonFile.is_file():
            Err = "Given JSON file not found!"
            raise RuntimeError(Err)

        with jsonFile.open() as JSONInput:
            try:
                JSONContent = json.load(JSONInput)

            except json.JSONDecodeError as e:
                Err = "Could not decode JSON config file!"
                raise RuntimeError from e

        # SCHEMA CHECK
        IsSchemaValid = True
        MatchKeys = {
            "showDir",
            "showName",
            "appendix",
            "filetype",
            "sep",
            "episode",
            "season",
            "version",
        }
        if set(JSONContent.keys()) != MatchKeys:
            IsSchemaValid = False

        EpisodeKeys = {"regex", "offset", "position", "largest"}
        if set(JSONContent["episode"].keys()) != EpisodeKeys:
            IsSchemaValid = False

        SeasonKeys = EpisodeKeys - {"largest"}
        if set(JSONContent["season"].keys()) != SeasonKeys:
            IsSchemaValid = False

        if set(JSONContent["version"].keys()) != SeasonKeys:
            IsSchemaValid = False

        if not IsSchemaValid:
            Err = "Malformed config JSON file!"
            raise RuntimeError(Err)

        # POPULATE
        self.ShowDir = Path(JSONContent["showDir"])
        self.ShowName = JSONContent["showName"]
        self.FileExtension = JSONContent["filetype"]
        self.SepStr = JSONContent["sep"]

        self.Appendix = JSONContent["appendix"]

        self.EpisodeRegex = JSONContent["episode"]["regex"]
        self.EpisodePosition = int(JSONContent["episode"]["position"])
        self.EpisodeOffset = int(JSONContent["episode"]["offset"])
        self.EpisodeLargest = int(JSONContent["episode"]["largest"])

        self.SeasonRegex = JSONContent["season"]["regex"]
        self.SeasonPosition = int(JSONContent["season"]["position"])
        self.SeasonOffset = int(JSONContent["season"]["offset"])

        self.SpecialVerRegex = JSONContent["version"]["regex"]
        self.SpecialVerPosition = int(JSONContent["version"]["position"])
        self.SpecialVerOffset = int(JSONContent["version"]["offset"])

    def save_settings(self, configFile: Path) -> None:
        """Save config settings to a JSON file.

        Args:
            configFile (Path): Output JSON file
        """
        JSONConfig = {}

        JSONConfig["showDir"] = str(self.ShowDir.absolute())
        JSONConfig["showName"] = self.ShowName
        JSONConfig["filetype"] = self.FileExtension
        JSONConfig["sep"] = self.SepStr

        JSONConfig["appendix"] = self.Appendix

        JSONConfig["episode"] = {}
        JSONConfig["episode"]["regex"] = self.EpisodeRegex
        JSONConfig["episode"]["position"] = self.EpisodePosition
        JSONConfig["episode"]["offset"] = self.EpisodeOffset
        JSONConfig["episode"]["largest"] = self.EpisodeLargest

        JSONConfig["season"] = {}
        JSONConfig["season"]["regex"] = self.SeasonRegex
        JSONConfig["season"]["position"] = self.SeasonPosition
        JSONConfig["season"]["offset"] = self.SeasonOffset

        JSONConfig["version"] = {}
        JSONConfig["version"]["regex"] = self.SpecialVerRegex
        JSONConfig["version"]["position"] = self.SpecialVerPosition
        JSONConfig["version"]["offset"] = self.SpecialVerOffset

        with configFile.open("w") as JSONOut:
            json.dump(JSONConfig, JSONOut, indent=4)
