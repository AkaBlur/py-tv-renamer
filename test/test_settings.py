import json
import pytest

from tv_renamer.settings import BatchSettings


def test_batch_settings_init():
    TestSettings = BatchSettings()

    assert TestSettings.ShowName == ""
    assert TestSettings.FileExtension == ""
    assert TestSettings.SepStr == ""

    assert TestSettings.Appendix == ""

    assert TestSettings.EpisodeRegex == ""
    assert type(TestSettings.EpisodePosition) is int
    assert TestSettings.EpisodePosition == 0
    assert type(TestSettings.EpisodeOffset) is int
    assert TestSettings.EpisodeOffset == 0
    assert type(TestSettings.EpisodeLargest) is int
    assert TestSettings.EpisodeLargest == 99

    assert TestSettings.SeasonRegex == ""
    assert type(TestSettings.SeasonPosition) is int
    assert TestSettings.SeasonPosition == 0
    assert type(TestSettings.SeasonOffset) is int
    assert TestSettings.SeasonOffset == 0

    assert TestSettings.SpecialVerRegex == ""
    assert type(TestSettings.SpecialVerPosition) is int
    assert TestSettings.SpecialVerPosition == 0
    assert type(TestSettings.SpecialVerOffset) is int
    assert TestSettings.SpecialVerOffset == 0


def test_load_settings(inst_basic_settings, default_settings_json):
    # read values are assumed to be set correctly inside default.json
    inst_basic_settings.load_settings(default_settings_json)


def test_load_settings_no_file(tmp_path, inst_basic_settings):
    # not on disk
    TestNoFile = tmp_path / "not_existing.json"
    assert not TestNoFile.exists()

    with pytest.raises(RuntimeError):
        inst_basic_settings.load_settings(TestNoFile)

    # not a file
    TestNoFile.mkdir()
    assert TestNoFile.exists()
    assert TestNoFile.is_dir()

    with pytest.raises(RuntimeError):
        inst_basic_settings.load_settings(TestNoFile)


def test_load_settings_json_error(tmp_path, inst_basic_settings):
    TestNoJSON = tmp_path / "no_json.json"
    with TestNoJSON.open("w") as FakeJSON:
        FakeJSON.write("wrong format!")

    assert TestNoJSON.exists()
    assert TestNoJSON.is_file()

    with pytest.raises(RuntimeError):
        inst_basic_settings.load_settings(TestNoJSON)


@pytest.mark.parametrize(
    "missingEntry",
    [
        "showDir",
        "showName",
        "appendix",
        "filetype",
        "sep",
        "episode/regex",
        "episode/offset",
        "episode/position",
        "episode/largest",
        "season/regex",
        "season/offset",
        "season/position",
        "version/regex",
        "version/offset",
        "version/position",
        None,
    ],
)
def test_load_settings_schema_check(
    tmp_path, inst_basic_settings, missingEntry, default_settings_json
):
    with default_settings_json.open("r") as JSONIn:
        ValidSettings = json.load(JSONIn)

    # invalidate settings dict
    IsValid = True
    if missingEntry:
        IsValid = False
        if "/" in missingEntry:
            Entries = missingEntry.split("/")
            ValidSettings[Entries[0]].pop(Entries[1])

        else:
            ValidSettings.pop(missingEntry)

    TestSettings = tmp_path / "settings.json"
    with TestSettings.open("w") as JSONOutput:
        json.dump(ValidSettings, JSONOutput)

    assert TestSettings.exists()
    assert TestSettings.is_file()

    if not IsValid:
        with pytest.raises(RuntimeError):
            inst_basic_settings.load_settings(TestSettings)

    else:
        inst_basic_settings.load_settings(TestSettings)


@pytest.mark.parametrize(
    ("entry", "wrongType"),
    [
        ("episode/position", "wrong"),
        ("episode/offset", "wrong"),
        ("episode/largest", "wrong"),
        ("season/position", "wrong"),
        ("season/offset", "wrong"),
        ("version/position", "wrong"),
        ("version/offset", "wrong"),
    ],
)
def test_load_settings_wrong_type(
    tmp_path, inst_basic_settings, default_settings_json, entry, wrongType
):
    with default_settings_json.open("r") as JSONIn:
        ValidSettings = json.load(JSONIn)

    if "/" in entry:
        Entries = entry.split("/")
        ValidSettings[Entries[0]][Entries[1]] = wrongType

    else:
        ValidSettings[entry] = wrongType

    TestSettings = tmp_path / "settings.json"
    with TestSettings.open("w") as JSONOutput:
        json.dump(ValidSettings, JSONOutput)

    assert TestSettings.exists()
    assert TestSettings.is_file()

    with pytest.raises(RuntimeError):
        inst_basic_settings.load_settings(TestSettings)


def test_save_settings(tmp_path, inst_basic_settings, default_settings_json):
    # test setup
    TestOutput = tmp_path / "settings.json"
    assert not TestOutput.exists()

    inst_basic_settings.load_settings(default_settings_json)
    with default_settings_json.open("r") as JSONIn:
        TestSettings = json.load(JSONIn)

    # save testing
    inst_basic_settings.save_settings(TestOutput)

    assert TestOutput.exists()
    assert TestOutput.is_file()

    # format testing
    with TestOutput.open("r") as JSONIn:
        CheckSettings = json.load(JSONIn)

    assert type(CheckSettings) is dict
    assert TestSettings.keys() == CheckSettings.keys()
