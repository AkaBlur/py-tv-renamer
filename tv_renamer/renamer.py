import dataclasses
import enum
import math
from pathlib import Path
import re

from . import settings, util


class RenamerError(enum.Enum):
    NO_ERROR = 0

    SEPARATOR_NOT_FOUND = 5

    EPISODE_POS_NOT_FOUND = 10
    SEASON_POS_NOT_FOUND = 11
    VERSION_POS_NOT_FOUND = 12

    EPISODE_NOT_FOUND = 20
    SEASON_NOT_FOUND = 21

    EPISODE_NUMBER_INVALID = 30
    SEASON_NUMBER_INVALID = 31
    VERSION_NUMBER_INVALID = 32

    RENAMING_DUPLICATES = 40
    RENAMING_FILEPATH_ERROR = 41


def get_error_representation(error: RenamerError) -> str:
    ErrName = error.name
    ErrorList = {
        "NO_ERROR": "No Error",
        "SEPARATOR_NOT_FOUND": "Given separator not contained in filename!",
        "EPISODE_POS_NOT_FOUND": "Episode position exhaust given filename!",
        "SEASON_POS_NOT_FOUND": "Season position exhaust given filename!",
        "VERSION_POS_NOT_FOUND": "Special Version position exhaust given filename!",
        "EPISODE_NOT_FOUND": "Episode number not found in filename!",
        "SEASON_NOT_FOUND": "Season number not found in filename!",
        "EPISODE_NUMBER_INVALID": "Episode number incorrectly formatted!",
        "SEASON_NUMBER_INVALID": "Season number incorrectly formatted!",
        "VERSION_NUMBER_INVALID": "Special Version number incorrectly formatted!",
        "RENAMING_DUPLICATES": "Attempt to rename duplicate filenames!",
        "RENAMING_FILEPATH_ERROR": "Could not rename file!",
    }

    if ErrorList.get(ErrName) is not None:
        return ErrorList[ErrName]

    return "Undefined Error!"


@dataclasses.dataclass
class SeasonEpisodeResult:
    ResultState: RenamerError

    Episode: int = 0
    Season: int = 0
    SpecialVer: int = 0

    CurrentName: str = ""
    ReformattedName: str = ""


def extract_season_episode(  # noqa: C901
    avFilepath: Path, settings: settings.BatchSettings
) -> SeasonEpisodeResult:
    """Extract episode and season information from the given file.

    Episode and Season must be extractable. A special revision number can be
    optionally extracted.

    Args:
        avFilepath (Path): Filepath for show file
        settings (settings.BatchSettings): Main application settings

    Returns:
        SeasonEpisodeResult: Result of extraction
    """
    Filename = avFilepath.name
    if settings.SepStr not in Filename:
        return SeasonEpisodeResult(ResultState=RenamerError.SEPARATOR_NOT_FOUND)

    FilenameSplits = Filename.split(settings.SepStr)

    # check validity for indexing
    if len(FilenameSplits) <= settings.EpisodePosition:
        return SeasonEpisodeResult(ResultState=RenamerError.EPISODE_POS_NOT_FOUND)

    if len(FilenameSplits) <= settings.SeasonPosition:
        return SeasonEpisodeResult(ResultState=RenamerError.SEASON_POS_NOT_FOUND)

    if len(FilenameSplits) <= settings.SpecialVerPosition:
        return SeasonEpisodeResult(ResultState=RenamerError.VERSION_POS_NOT_FOUND)

    # regex construction
    EpisodePart = FilenameSplits[settings.EpisodePosition]
    EpisodeReg = re.search(settings.EpisodeRegex, EpisodePart)

    if EpisodeReg is None:
        return SeasonEpisodeResult(ResultState=RenamerError.EPISODE_NOT_FOUND)

    SeasonPart = FilenameSplits[settings.SeasonPosition]
    SeasonReg = re.search(settings.SeasonRegex, SeasonPart)

    if SeasonReg is None:
        return SeasonEpisodeResult(ResultState=RenamerError.SEASON_NOT_FOUND)

    SpecialVerPart = FilenameSplits[settings.SpecialVerPosition]
    SpecialVerReg = re.search(settings.SpecialVerRegex, SpecialVerPart)

    # value extraction
    Episode = 0
    try:
        Episode = int(EpisodeReg.group(1))

    except ValueError:
        return SeasonEpisodeResult(ResultState=RenamerError.EPISODE_NUMBER_INVALID)

    Season = 0
    try:
        Season = int(SeasonReg.group(1))

    except ValueError:
        return SeasonEpisodeResult(ResultState=RenamerError.SEASON_NUMBER_INVALID)

    if SpecialVerReg is not None:
        SpecialVersion = 0
        try:
            SpecialVersion = int(SpecialVerReg.group(1))

        except ValueError:
            return SeasonEpisodeResult(ResultState=RenamerError.VERSION_NUMBER_INVALID)

    else:
        SpecialVersion = 1

    return SeasonEpisodeResult(
        ResultState=RenamerError.NO_ERROR,
        Episode=Episode + settings.EpisodeOffset,
        Season=Season + settings.SeasonOffset,
        SpecialVer=SpecialVersion + settings.SpecialVerOffset,
    )


def list_season_episode(
    appSettings: settings.BatchSettings,
) -> list[SeasonEpisodeResult]:
    """Scan given directory for show files to extraction and reformat.

    Will only list files with respected formatted name. All files must have a
    valid format according to given settings!

    Results may contain elements from invalid extraction results.

    Args:
        appSettings (settings.BatchSettings): Main app settings

    Returns:
        list[SeasonEpisodeResult]: List of renamer results
    """
    # BUG: detection of multi-episode files not possible currently
    # e.g.: E19-E21 is probably detected as E19 (according to given regex)
    # multiple capture groups are not taken into account
    ResultList: list[SeasonEpisodeResult] = []

    for File in appSettings.ShowDir.rglob(f"*.{appSettings.FileExtension}"):
        # check for file
        if util.check_file(File) != util.PathError.CORRECT:
            continue

        ExtractInfo = extract_season_episode(File, appSettings)
        ExtractInfo.CurrentName = File.name

        # validity of extraction
        if ExtractInfo.ResultState != RenamerError.NO_ERROR:
            ResultList.append(ExtractInfo)
            continue

        # calculate number of necessary filler zeros
        NumZeros = math.log10(appSettings.EpisodeLargest)
        NumZeros = math.ceil(NumZeros)
        NumZeros = int(NumZeros)

        # construct new name
        EpisodeStr = str(ExtractInfo.Episode)
        if len(EpisodeStr) < NumZeros:
            EpisodeFill = ("").join(["0" for _ in range(NumZeros - len(EpisodeStr))])
            EpisodeStr = EpisodeFill + EpisodeStr

        # some revision on file
        if ExtractInfo.SpecialVer > 1:
            ExtractInfo.ReformattedName = f"{appSettings.ShowName} - S{ExtractInfo.Season}E{EpisodeStr}_V{ExtractInfo.SpecialVer}- {appSettings.Appendix}.{appSettings.FileExtension}"  # noqa: E501

        else:
            ExtractInfo.ReformattedName = f"{appSettings.ShowName} - S{ExtractInfo.Season}E{EpisodeStr} - {appSettings.Appendix}.{appSettings.FileExtension}"  # noqa: E501

        ResultList.append(ExtractInfo)

    return ResultList


def rename_files(
    appSettings: settings.BatchSettings, scanOutput: list[SeasonEpisodeResult]
) -> RenamerError:
    """Batch rename all files from a successful scan. Will skip files that are
    not correctly matched to prevent failures.

    Args:
        appSettings (settings.BatchSettings): Main application settings
        scanOutput (list[SeasonEpisodeResult]): List of scan results

    Returns:
        RenamerError: Result state from renaming
    """
    CurFiles = [Res.CurrentName for Res in scanOutput]
    NewFiles = [Res.ReformattedName for Res in scanOutput]

    if len(set(CurFiles) & set(NewFiles)) >= 1:
        return RenamerError.RENAMING_DUPLICATES

    for Entry in scanOutput:
        if Entry.ResultState != RenamerError.NO_ERROR:
            continue

        CurPath = appSettings.ShowDir / Entry.CurrentName
        NewPath = appSettings.ShowDir / Entry.ReformattedName

        try:
            CurPath.rename(NewPath)

        except OSError:
            return RenamerError.RENAMING_FILEPATH_ERROR

    return RenamerError.NO_ERROR
