### Project README

A detailed guide to the repository test automation, Selenium UI tests, and the provided test runner scripts for local and CI usage.

---

### Overview
**What this repo contains**  
- **Selenium UI tests** that exercise the Dash app UI using headless Chrome.  
- **Two test runner scripts**: `scripts/run_tests.ps1` for PowerShell and `scripts/run_tests.sh` for Bash.  
- **A Selenium test file** `tests/test_dash_ui_selenium.py` that uses `webdriver-manager` to obtain a matching ChromeDriver.  
- **Legacy tests** `tests/test_dash_ui.py` that may expect `chromedriver.exe` on PATH.  
**Goal**  
Make it easy to run the full test suite locally and in CI with minimal manual setup.

---

### Prerequisites
**Required software**  
- **Python 3.8+** installed and available on PATH.  
- **Git** for repository operations.  
- **Google Chrome** installed for Selenium tests.  
**Python packages**  
Install into a virtual environment using one of these commands:

```bash
python -m venv .venv
# activate the venv then
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
# or if no requirements file
python -m pip install pytest selenium webdriver-manager requests
```

**Notes about ChromeDriver**  
- Tests using `webdriver-manager` will download a compatible ChromeDriver automatically.  
- Some tests expect `chromedriver.exe` on PATH. The repository includes helper steps to copy the webdriver-manager cached binary to `C:\tools\chromedriver` and add it to PATH for Windows sessions.

---

### Running tests locally
#### Using the PowerShell runner
**Run from repository root in PowerShell**:

```powershell
# allow script execution for this session
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# run the test runner
.\scripts\run_tests.ps1
```

**What the script does**  
- Attempts to activate a venv in `.venv`, `venv`, or `env`.  
- Installs missing test dependencies if `pytest` is not present.  
- Runs `python -m pytest -q`.  
- Exits with code **0** on success and **1** on failure.

#### Using the Bash runner
**Run from repository root on Unix like systems or Git Bash**:

```bash
chmod +x scripts/run_tests.sh
./scripts/run_tests.sh
```

**What the script does**  
- Attempts to source a venv in `.venv`, `venv`, or `env`.  
- Installs test dependencies if missing.  
- Runs `python -m pytest -q`.  
- Exits with code **0** on success and **1** on failure.

#### Running pytest directly
If you prefer to run tests manually:

```bash
# activate your venv first
python -m pytest -q
```

---

### How the Selenium tests work
**Key files**  
- `tests/test_dash_ui_selenium.py` uses `webdriver-manager` to install a ChromeDriver and launches headless Chrome.  
- `tests/test_dash_ui.py` contains additional UI checks and may rely on `chromedriver.exe` being on PATH.  
**Best practice**  
Prefer tests that use `webdriver-manager` because they automatically download the correct driver for the installed Chrome version and are more CI friendly.

---

### CI integration example
**GitHub Actions example**  
Create `.github/workflows/ci.yml` with the following steps to run tests on Windows using the PowerShell runner:

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Create virtualenv and install deps
        run: |
          python -m venv .venv
          .\.venv\Scripts\Activate.ps1
          pip install -r requirements.txt || pip install pytest selenium webdriver-manager requests
      - name: Run tests
        run: .\scripts\run_tests.ps1
```

**Notes for CI**  
- Use `windows-latest` if you rely on `chromedriver.exe` on PATH.  
- `webdriver-manager` works on Linux and Windows and is recommended to avoid manual driver management.  
- If CI runners do not have Chrome, install Chrome or use a container image that includes Chrome.

---

### Troubleshooting
**Common issues and fixes**

- **ModuleNotFoundError webdriver_manager**  
  - Ensure the venv is activated and run `python -m pip install webdriver-manager` inside the venv.

- **chromedriver executable needs to be in PATH**  
  - Use `webdriver-manager` in tests or copy the cached chromedriver to `C:\tools\chromedriver` and add it to PATH for the session:
    ```powershell
    # example commands to copy cached chromedriver to C:\tools\chromedriver
    python -c "from webdriver_manager.chrome import ChromeDriverManager; print(ChromeDriverManager().install())"
    ```
  - Persist the folder to User PATH if desired.

- **Dash server not reachable in tests**  
  - Ensure no other process uses port `8050`. Change the port in the test `server` fixture and update `driver.get(...)` accordingly.

- **Slow rendering or flaky tests**  
  - Increase `WebDriverWait` timeouts in tests.  
  - Ensure the machine has sufficient CPU and memory for headless Chrome.

- **Proxy or network restrictions block webdriver-manager**  
  - Download the correct ChromeDriver manually and point tests to the local executable using `Service(r"C:\path\chromedriver.exe")`.

**How to collect useful logs**  
- Re-run pytest with verbose output:
  ```bash
  python -m pytest -q -k test_name -s
  ```
- Inspect ChromeDriver logs by launching the driver with logging options in the test if needed.

---

### Files added by this task
- **`tests/test_dash_ui_selenium.py`** Selenium tests using `webdriver-manager`.  
- **`scripts/run_tests.ps1`** PowerShell test runner.  
- **`scripts/run_tests.sh`** Bash test runner.  

---

### Final notes
- **Exit codes**: Both runners return **0** on success and **1** on failure.  
- **Recommendation**: Prefer `webdriver-manager` in tests to avoid manual driver management.  
- **CI readiness**: The provided scripts and the GitHub Actions example make it straightforward to run the test suite automatically on push.

---
