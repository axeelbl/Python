# Python mini-projects

Three small graphical projects for practising Python fundamentals. Each script remains directly
executable, while its core logic can also be imported and tested without opening a window.

## Projects

- **`Calculator.py`** — Tkinter calculator supporting arithmetic, parentheses, `pi`, `sqrt` and
  natural logarithms. Expressions are interpreted by a restricted AST evaluator; arbitrary Python
  code is never executed.
- **`FidgetSpinner.py`** — turtle animation controlled with the space bar.
- **`SolarSystem.py`** — pygame visualisation of a simplified Newtonian five-body system. Bodies
  are advanced from the same state on every frame, and orbit trails have a bounded history.

These are educational visualisations, not precision scientific or financial tools. The solar model
uses a one-day Euler integration step and intentionally omits many real-world effects.

## Requirements

- Python 3.10 or newer
- Tk support for the calculator and turtle demos (on Debian/Ubuntu: `python3-tk`)
- A graphical desktop session

Create an isolated environment and install the only third-party runtime dependency:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

No environment variables or credentials are required, so this repository intentionally has no
`.env.example`.

## Usage

Run one project at a time:

```bash
python Calculator.py
python FidgetSpinner.py
python SolarSystem.py
```

Press **space** repeatedly to accelerate the spinner. Close the active window to stop a project.

## Development

Install the development tools and run the same checks as CI:

```bash
python -m pip install -r requirements-dev.txt
python -m ruff check .
python -m ruff format --check .
python -m compileall -q Calculator.py FidgetSpinner.py SolarSystem.py tests scripts
python -m pytest
python -m pip_audit -r requirements.txt
python -m pip_audit --local
python scripts/check_repository.py
```

Tests cover safe expression evaluation, import behaviour, spinner state, simultaneous orbital
updates, physical validation, and bounded trail storage. GUI appearance and event handling still
need a desktop smoke test.

## Structure

```text
.
├── Calculator.py
├── FidgetSpinner.py
├── SolarSystem.py
├── requirements.txt
├── requirements-dev.txt
├── scripts/check_repository.py
└── tests/
```

## License

Released under the [MIT License](LICENSE).
