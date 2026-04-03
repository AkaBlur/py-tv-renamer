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

    return TestSettings
