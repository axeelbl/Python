import subprocess
import sys


def test_modules_import_without_starting_graphical_loops() -> None:
    result = subprocess.run(
        [sys.executable, "-c", "import Calculator, FidgetSpinner, SolarSystem"],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
