from pathlib import Path
import pytest

from tv_renamer.settings import BatchSettings


@pytest.fixture
def default_settings_json() -> Path:
    TestFile = Path(__file__).parent.parent
    TestFile /= "tv_renamer"
    TestFile /= "default.json"

    if not TestFile.exists():
        pytest.fail("default.json configuration not found in project directory!")

    return TestFile


@pytest.fixture
def inst_basic_settings() -> BatchSettings:
    return BatchSettings()


@pytest.fixture
def inst_default_settings(default_settings_json) -> BatchSettings:
    TestSettings = BatchSettings()
    TestSettings.load_settings(default_settings_json)

    # corresponds to following definitions of test-files
    TestSettings.EpisodePosition = 1
    TestSettings.SeasonPosition = 1
    TestSettings.SpecialVerPosition = 1

    return TestSettings


@pytest.fixture
def sample_filenames_correct() -> list[str]:
    # must all map to different renamer results
    return [
        "Show - S01E01.mkv",
        "Show - S01 E02.mkv",
        "Show - S1 E03.mkv",
        "Show - S1 E4.mkv",
        "Show - S1 E100.mkv",
        "Show - S102 E100.mkv",
        "Show - S102E101.mkv",
        "Show - S102123123123E100.mkv",
        "Show - S0v1E100.mkv",
        "Show - E01S05.mkv",
        "Show - E01 S02.mkv",
        "Show - E01 S03 [somthing].mkv",
        "Show - E01 S04 _V1[somthing].mkv",
        "Show - E01 S01 _V2[somthing].mkv",
        "Show - _V1 E02 S02[somthing].mkv",
    ]


@pytest.fixture
def sample_files_correct(tmp_path, sample_filenames_correct) -> list[Path]:
    MockShowDir = tmp_path / "Show"
    MockShowDir.mkdir()

    MockFiles: list[Path] = []
    for File in sample_filenames_correct:
        MockFiles.append(MockShowDir / File)
        MockFiles[-1].touch()

    return MockFiles
