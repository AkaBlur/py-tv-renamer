import pytest

from tv_renamer import util
from tv_renamer.util import PathError


def test_check_dir(tmp_path):
    TestPath = tmp_path / "testing"
    TestPath.mkdir()
    assert TestPath.is_dir()

    CheckError = util.check_dir(TestPath)
    assert CheckError == PathError.CORRECT


def test_check_dir_wrong(tmp_path):
    # doesn't exist
    TestPath = tmp_path / "testing"
    assert not TestPath.exists()

    CheckError = util.check_dir(TestPath)
    assert CheckError == PathError.NOT_EXISTING

    # no dir
    TestPath.touch()
    assert TestPath.is_file()

    CheckError = util.check_dir(TestPath)
    assert CheckError == PathError.WRONG_TYPE


def test_check_file(tmp_path):
    TestPath = tmp_path / "testing"
    TestPath.touch()
    assert TestPath.is_file()

    CheckError = util.check_file(TestPath)
    assert CheckError == PathError.CORRECT


def test_check_file_wrong(tmp_path):
    # doesn't exist
    TestPath = tmp_path / "testing"
    assert not TestPath.exists()

    CheckError = util.check_file(TestPath)
    assert CheckError == PathError.NOT_EXISTING

    # no file
    TestPath.mkdir()
    assert TestPath.is_dir()

    CheckError = util.check_file(TestPath)
    assert CheckError == PathError.WRONG_TYPE


@pytest.mark.parametrize(
    ("isValid", "testValue"),
    [
        (False, "wrong"),
        (True, 1e2),
        (True, 0.5),
        (False, None),
    ],
)
def test_safe_convert_int(isValid, testValue):
    if isValid:
        TestOutput = int(testValue)

        CheckOutput = util.safe_convert_int(testValue)

        assert CheckOutput == TestOutput

    else:
        CheckOutput = util.safe_convert_int(testValue)

        assert CheckOutput == 0
