from pathlib import Path
import sys

from . import app


def run() -> None:  # pragma: no cover
    """Application startup"""
    # set working directory to supplied directory if correct
    if len(sys.argv) == 2 and Path(sys.argv[1]).exists() and Path(sys.argv[1]).is_dir():  # noqa : PLR2004
        App = app.RenamerApp(Path(sys.argv[1]))

    else:
        App = app.RenamerApp()

    App.load_settings()
    App.register_callbacks()

    App.run()

    App.shutdown()
