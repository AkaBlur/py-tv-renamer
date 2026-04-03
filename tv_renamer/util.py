import contextlib
import enum
from pathlib import Path


class PathError(enum.Enum):
    CORRECT = 0
    NOT_EXISTING = 1
    WRONG_TYPE = 2


def check_dir(dirPath: Path) -> PathError:
    """Check if a directory exists and is valid directory.

    Args:
        dirPath (Path): Directory to check

    Returns:
        PathError: Return info
    """
    if not dirPath.exists():
        return PathError.NOT_EXISTING

    if not dirPath.is_dir():
        return PathError.WRONG_TYPE

    return PathError.CORRECT


def check_file(filePath: Path) -> PathError:
    """Check if a file exists and is valid file.

    Args:
        filePath (Path): File to check

    Returns:
        PathError: Return info
    """
    if not filePath.exists():
        return PathError.NOT_EXISTING

    if not filePath.is_file():
        return PathError.WRONG_TYPE

    return PathError.CORRECT


def safe_convert_int(inputStr: str) -> int:
    """Safely convert str to int. On error will return 0.

    Args:
        inputStr (str): Input string

    Returns:
        int: Converted integer
    """
    Output = 0

    with contextlib.suppress(ValueError, TypeError):
        Output = int(inputStr)

    return Output
