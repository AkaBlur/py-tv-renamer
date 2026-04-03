from pathlib import Path
import sys

from . import app


def run() -> None:
    """Application startup"""
    WorkPath: Path = None
    if len(sys.argv) == 2 and Path(sys.argv[1]).exists() and Path(sys.argv[1]).is_dir():  # noqa : PLR2004
        WorkPath = Path(sys.argv[1])

    App = app.RenamerApp(Path(WorkPath)) if WorkPath is not None else app.RenamerApp()

    App.load_settings()
    App.register_callbacks()

    App.run()

    App.shutdown()
