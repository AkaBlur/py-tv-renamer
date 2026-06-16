import enum
from pathlib import Path
import pytest

from tv_renamer import renamer
from tv_renamer.renamer import RenamerError


# ------------------------------------------------------------------------------
# RENAMER RESULT
# ------------------------------------------------------------------------------
class FakeError(enum.Enum):
    FAKE_ERROR = 0


@pytest.mark.parametrize(
    ("error", "isValid"),
    [
        (RenamerError.NO_ERROR, True),
        (RenamerError.SEPARATOR_NOT_FOUND, True),
        (RenamerError.EPISODE_POS_NOT_FOUND, True),
        (RenamerError.SEASON_POS_NOT_FOUND, True),
        (RenamerError.VERSION_POS_NOT_FOUND, True),
        (RenamerError.EPISODE_NOT_FOUND, True),
        (RenamerError.SEASON_NOT_FOUND, True),
        (RenamerError.EPISODE_NUMBER_INVALID, True),
        (RenamerError.SEASON_NUMBER_INVALID, True),
        (RenamerError.VERSION_NUMBER_INVALID, True),
        (RenamerError.RENAMING_DUPLICATES, True),
        (RenamerError.RENAMING_FILEPATH_ERROR, True),
        (FakeError.FAKE_ERROR, False),
    ],
)
def test_get_error_repr(error, isValid):
    CheckErrorRepr = renamer.get_error_representation(error)

    assert (CheckErrorRepr != "Undefined Error!") == isValid


# ------------------------------------------------------------------------------
# EXTRACTION LOGIC
# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("testFilename", "episode", "season", "version"),
    [
        ("Show - S01E01.mkv", 1, 1, 1),
        ("Show - S01 E01.mkv", 1, 1, 1),
        ("Show - S1 E01.mkv", 1, 1, 1),
        ("Show - S1 E1.mkv", 1, 1, 1),
        ("Show - S1 E100.mkv", 100, 1, 1),
        ("Show - S1 E100 - E2.mkv", 100, 1, 1),
        ("Show - S1 E100 - S2.mkv", 100, 1, 1),
        ("Show - S102 E100.mkv", 100, 102, 1),
        ("Show - S102E100.mkv", 100, 102, 1),
        ("Show - S102123123123E100.mkv", 100, 102123123123, 1),
        ("Show - S0v1E100.mkv", 100, 0, 1),
        ("Show - E01S01.mkv", 1, 1, 1),
        ("Show - E01 S01.mkv", 1, 1, 1),
        ("Show - E01 S01 [somthing].mkv", 1, 1, 1),
        ("Show - E01 S01 v1[somthing].mkv", 1, 1, 1),
        ("Show - v1 E01 S01[somthing].mkv", 1, 1, 1),
        ("Show - E01 S01_V1[somthing].mkv", 1, 1, 1),
        ("Show - S01E01_V9000 [somthing].mkv", 1, 1, 9000),
        ("Show - S01E01_V9000 - _V2 [somthing].mkv", 1, 1, 9000),
    ],
)
def test_extract_season_episode(
    testFilename, inst_default_settings, episode, season, version
):
    TestFile = Path(testFilename)
    # set regex positions to "1"
    inst_default_settings.EpisodePosition = 1
    inst_default_settings.SeasonPosition = 1
    inst_default_settings.SpecialVerPosition = 1

    CheckResult = renamer.extract_season_episode(TestFile, inst_default_settings)

    assert type(CheckResult) is renamer.SeasonEpisodeResult
    assert CheckResult.ResultState == RenamerError.NO_ERROR
    assert CheckResult.Episode == episode
    assert type(CheckResult.Episode) is int
    assert CheckResult.Season == season
    assert type(CheckResult.Season) is int
    assert CheckResult.SpecialVer == version
    assert type(CheckResult.SpecialVer) is int

    assert CheckResult.CurrentName == testFilename
    assert CheckResult.ReformattedName == ""


@pytest.mark.parametrize(
    ("testFilename", "result"),
    [
        # NO_ERROR
        ("Show - S01E01.mkv", RenamerError.NO_ERROR),
        ("Show - S01 E01.mkv", RenamerError.NO_ERROR),
        ("Show - S1 E01.mkv", RenamerError.NO_ERROR),
        ("Show - S1 E1.mkv", RenamerError.NO_ERROR),
        ("Show - S1 E100.mkv", RenamerError.NO_ERROR),
        ("Show - S102 E100.mkv", RenamerError.NO_ERROR),
        ("Show - S102E100.mkv", RenamerError.NO_ERROR),
        ("Show - S102123123123E100.mkv", RenamerError.NO_ERROR),
        ("Show - S0v1E100.mkv", RenamerError.NO_ERROR),
        ("Show - E01S01.mkv", RenamerError.NO_ERROR),
        ("Show - E01 S01.mkv", RenamerError.NO_ERROR),
        ("Show - E01 S01 [somthing].mkv", RenamerError.NO_ERROR),
        ("Show - E01 S01 v1[somthing].mkv", RenamerError.NO_ERROR),
        ("Show - v1 E01 S01[somthing].mkv", RenamerError.NO_ERROR),
        # SEPARATOR_NOT_FOUND
        ("Show.S01E01.mkv", RenamerError.SEPARATOR_NOT_FOUND),
        ("Show S01E01.mkv", RenamerError.SEPARATOR_NOT_FOUND),
        ("Show|S01E01.mkv", RenamerError.SEPARATOR_NOT_FOUND),
        # EPISODE_NOT_FOUND
        ("Show - S01e01 - E01.mkv", RenamerError.EPISODE_NOT_FOUND),
        ("Show - - S01E01.mkv", RenamerError.EPISODE_NOT_FOUND),
        ("Show - Extra - S01E01.mkv", RenamerError.EPISODE_NOT_FOUND),
        ("Show - S01 - E01.mkv", RenamerError.EPISODE_NOT_FOUND),
        # SEASON_NOT_FOUND
        ("Show - s01E01 - E01.mkv", RenamerError.SEASON_NOT_FOUND),
        ("Show - E01 - S01.mkv", RenamerError.SEASON_NOT_FOUND),
    ],
)
def test_extract_season_episode_error_types(
    inst_default_settings, testFilename, result
):
    TestFile = Path(testFilename)
    # set regex positions to "1"
    inst_default_settings.EpisodePosition = 1
    inst_default_settings.SeasonPosition = 1
    inst_default_settings.SpecialVerPosition = 1

    CheckResult = renamer.extract_season_episode(TestFile, inst_default_settings)

    assert type(CheckResult) is renamer.SeasonEpisodeResult
    assert CheckResult.ResultState == result


@pytest.mark.parametrize(
    ("testFilename", "checking"),
    [
        ("Show - S01E01.mkv", 1),
        ("Show - S01 E01.mkv", 2),
        ("Show - E01S01.mkv", 3),
        ("Show - E01 S01.mkv", 1),
        ("Show - E01 S01 [somthing].mkv", 2),
        ("Show - S1 E01.mkv", 3),
        ("Show - S1 E1.mkv", 1),
        ("Show - S1 E100.mkv", 2),
        ("Show - S102 E100.mkv", 3),
        ("Show - S102E100.mkv", 1),
        ("Show - S102123123123E100.mkv", 2),
        ("Show - S0v1E100.mkv", 3),
        ("Show - E01 S01 v1[somthing].mkv", 1),
        ("Show - v1 E01 S01[somthing].mkv", 2),
        ("Show - V1 E01 S01[somthing].mkv", 3),
    ],
)
def test_extract_season_episode_pos_invalid(
    inst_default_settings, testFilename, checking
):
    TestFile = Path(testFilename)

    Result = None
    if checking == 1:
        inst_default_settings.EpisodePosition = 2
        Result = RenamerError.EPISODE_POS_NOT_FOUND

    elif checking == 2:
        inst_default_settings.SeasonPosition = 2
        Result = RenamerError.SEASON_POS_NOT_FOUND

    elif checking == 3:
        inst_default_settings.SpecialVerPosition = 2
        Result = RenamerError.VERSION_POS_NOT_FOUND

    else:
        pytest.fail("Wrong setting for index position!")

    CheckResult = renamer.extract_season_episode(TestFile, inst_default_settings)

    assert type(CheckResult) is renamer.SeasonEpisodeResult
    assert CheckResult.ResultState == Result


# would only apply to misconfigured regex inputs
@pytest.mark.parametrize(
    ("testFilename", "checking"),
    [
        ("Show - S01Ea01.mkv", 1),
        ("Show - S01gE01.mkv", 2),
        ("Show - S01E01_V1.mkv", 3),
    ],
)
def test_extract_season_episode_number_extraction_error(
    inst_default_settings, testFilename, checking
):
    TestFile = Path(testFilename)
    # set regex positions to "1"
    inst_default_settings.EpisodePosition = 1
    inst_default_settings.SeasonPosition = 1
    inst_default_settings.SpecialVerPosition = 1

    # includes only examples which would lead to a wrong extraction
    Result = None
    if checking == 1:
        inst_default_settings.EpisodeRegex = r"E([0-9a-z]+)"
        Result = RenamerError.EPISODE_NUMBER_INVALID

    elif checking == 2:
        inst_default_settings.SeasonRegex = r"S([0-9a-z]+)"
        Result = RenamerError.SEASON_NUMBER_INVALID

    elif checking == 3:
        inst_default_settings.SpecialVerRegex = r"(V[0-9a-z]+)"
        Result = RenamerError.VERSION_NUMBER_INVALID

    CheckResult = renamer.extract_season_episode(TestFile, inst_default_settings)

    assert type(CheckResult) is renamer.SeasonEpisodeResult
    assert CheckResult.ResultState == Result


# ------------------------------------------------------------------------------
# FILE INDEXER
# ------------------------------------------------------------------------------
def test_list_season_episode(
    sample_files_correct, sample_filenames_correct, inst_default_settings
):
    TestDir = sample_files_correct[0].parent

    inst_default_settings.ShowDir = TestDir

    CheckListResults = renamer.list_season_episode(inst_default_settings)

    assert type(CheckListResults) is list
    assert len(CheckListResults) == len(sample_filenames_correct)
    assert type(CheckListResults[0]) is renamer.SeasonEpisodeResult

    for CheckResult in CheckListResults:
        assert CheckResult.ResultState == renamer.RenamerError.NO_ERROR
        assert CheckResult.ReformattedName != ""


def test_list_season_episode_errors(tmp_path, inst_default_settings):
    MockFilenames = [
        # extraction errors
        "Show.S01E01.mkv",
        "Show S01E01.mkv",
        "Show - S01e01 - E01.mkv",
        "Show - - S01E01.mkv",
        "Show - Extra - S01E01.mkv",
        "Show - S01 - E01.mkv",
        "Show - E01 - S01.mkv",
    ]

    MockShowDir = tmp_path / "Show"
    MockShowDir.mkdir()
    # some misleading directories
    MockWrongFiles = [
        "Show - S01E01.mkv",
        "Show - S01 E01.mkv",
    ]

    for File in MockFilenames:
        MockFile = MockShowDir / File
        MockFile.touch()

    for Dir in MockWrongFiles:
        MockDir = MockShowDir / Dir
        MockDir.mkdir()

    inst_default_settings.ShowDir = MockShowDir

    CheckListResults = renamer.list_season_episode(inst_default_settings)

    assert type(CheckListResults) is list
    assert len(CheckListResults) == len(MockFilenames)
    assert type(CheckListResults[0]) is renamer.SeasonEpisodeResult

    for CheckResult in CheckListResults:
        assert CheckResult.ResultState != renamer.RenamerError.NO_ERROR


# ------------------------------------------------------------------------------
# RENAMER
# ------------------------------------------------------------------------------
def test_rename_files(
    sample_files_correct, sample_filenames_correct, inst_default_settings
):
    TestDir = sample_files_correct[0].parent
    inst_default_settings.ShowDir = TestDir

    inst_default_settings.ShowName = "Test"

    # generate file list
    TestResults = renamer.list_season_episode(inst_default_settings)

    assert type(TestResults) is list
    assert len(TestResults) == len(sample_filenames_correct)

    for CheckResult in TestResults:
        assert CheckResult.ResultState == renamer.RenamerError.NO_ERROR

    # rename
    CheckResult = renamer.rename_files(inst_default_settings, TestResults)
    assert CheckResult == renamer.RenamerError.NO_ERROR

    for File in TestDir.iterdir():
        assert File.exists()
        assert File.is_file()
        assert File.name.startswith("Test -")


def test_renamer_duplicates(inst_default_settings):
    # doesn't trigger the renamer
    TestDuplicates = renamer.SeasonEpisodeResult(
        ResultState=renamer.RenamerError.NO_ERROR,
        Episode=1,
        Season=1,
        SpecialVer=1,
        CurrentName="MyFile.mkv",
        ReformattedName="MyFile.mkv",
    )

    assert (
        renamer.rename_files(inst_default_settings, [TestDuplicates])
        == renamer.RenamerError.RENAMING_DUPLICATES
    )


def test_renamer_cant_rename(inst_default_settings):
    # doesn't trigger the renamer -> no file to rename
    TestDuplicates = renamer.SeasonEpisodeResult(
        ResultState=renamer.RenamerError.NO_ERROR,
        Episode=1,
        Season=1,
        SpecialVer=1,
        CurrentName="doesn't exist.mkv",
        ReformattedName="exist.mkv",
    )

    assert (
        renamer.rename_files(inst_default_settings, [TestDuplicates])
        == renamer.RenamerError.RENAMING_FILEPATH_ERROR
    )


def test_renamer_filter_error(inst_default_settings):
    # doesn't trigger error from renamer -> skip invalid renames
    TestErrors: list[renamer.SeasonEpisodeResult] = [
        renamer.SeasonEpisodeResult(
            ResultState=renamer.RenamerError.SEPARATOR_NOT_FOUND,
        ),
        renamer.SeasonEpisodeResult(
            ResultState=renamer.RenamerError.EPISODE_POS_NOT_FOUND,
        ),
        renamer.SeasonEpisodeResult(
            ResultState=renamer.RenamerError.SEASON_POS_NOT_FOUND, CurrentName="c.mkv"
        ),
        renamer.SeasonEpisodeResult(
            ResultState=renamer.RenamerError.VERSION_POS_NOT_FOUND, CurrentName="d.mkv"
        ),
        renamer.SeasonEpisodeResult(
            ResultState=renamer.RenamerError.EPISODE_NOT_FOUND, CurrentName="e.mkv"
        ),
        renamer.SeasonEpisodeResult(
            ResultState=renamer.RenamerError.SEASON_NOT_FOUND, CurrentName="f.mkv"
        ),
        renamer.SeasonEpisodeResult(
            ResultState=renamer.RenamerError.EPISODE_NUMBER_INVALID, CurrentName="g.mkv"
        ),
        renamer.SeasonEpisodeResult(
            ResultState=renamer.RenamerError.SEASON_NUMBER_INVALID, CurrentName="h.mkv"
        ),
        renamer.SeasonEpisodeResult(
            ResultState=renamer.RenamerError.VERSION_NUMBER_INVALID, CurrentName="i.mkv"
        ),
    ]

    assert (
        renamer.rename_files(inst_default_settings, TestErrors)
        == renamer.RenamerError.NO_ERROR
    )
