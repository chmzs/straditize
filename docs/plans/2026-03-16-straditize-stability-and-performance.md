# Straditize Stability And Performance Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make the local `straditize` project runnable in the current workspace, fix reproducible bugs, and land at least one evidence-backed performance improvement with passing feasibility checks.

**Architecture:** The package has a Python core (`straditize/straditize/*.py`) for diagram digitization plus a Qt-based GUI plugin layer (`straditize/straditize/widgets/*.py`). Work starts by restoring a valid local environment, then reproducing failures with targeted tests, then implementing minimal fixes in the core hot paths before running focused regression and smoke checks.

**Tech Stack:** Python 3.9, Pixi, pytest, PyQt5, matplotlib, numpy, pandas, scikit-image, xarray

---

### Task 1: Rebuild A Valid Test Baseline

**Files:**
- Modify: `pixi.toml`
- Test: `tests/`

**Step 1: Verify the current failure mode**

Run: `pixi run python -m pytest --version`
Expected: failure because `pytest` is missing

Run: `pixi run python -c "import pandas"`
Expected: failure because the installed pandas extensions do not match Python 3.9

**Step 2: Fix the local environment definition**

- Add the missing test/runtime dependencies required for local validation.
- Prefer making the environment reproducible from project configuration instead of relying on previously mutated site-packages.

**Step 3: Refresh the environment and re-run baseline checks**

Run: `pixi install`
Run: `pixi run python -m pytest --version`
Run: `pixi run python -c "import pandas; import straditize"`

Expected: imports succeed and pytest is available

### Task 2: Understand The Runtime Structure

**Files:**
- Read: `README.rst`
- Read: `setup.py`
- Read: `straditize/__main__.py`
- Read: `straditize/straditizer.py`
- Read: `straditize/binary.py`
- Test: `tests/test_binary.py`
- Test: `tests/test_straditizer.py`

**Step 1: Trace the main entry paths**

- CLI entry goes through `straditize.__main__.main()`
- Core workflow centers on `Straditizer` and `DataReader`
- Widget layer depends on the core but should not block core regressions from being tested

**Step 2: Identify one or two reproducible failures**

- Start with non-widget tests first
- Use widget tests only after the core baseline is stable

### Task 3: Reproduce Bugs With Targeted Tests

**Files:**
- Modify: `tests/test_binary.py`
- Modify: `tests/test_straditizer.py`
- Create if needed: `tests/test_regressions.py`

**Step 1: Add or tighten one failing regression test per bug**

- Each test should isolate one broken behavior
- Run the exact test and confirm it fails for the expected reason before implementation

**Step 2: Add a focused performance guard where practical**

- Prefer timing-independent assertions on call count, vectorization-friendly behavior, or avoided recomputation
- If a wall-clock benchmark is needed, keep it coarse and local to the hot path

### Task 4: Implement Minimal Fixes

**Files:**
- Modify: `straditize/binary.py`
- Modify: `straditize/straditizer.py`
- Modify other core modules only if evidence requires it

**Step 1: Fix the smallest root causes first**

- Keep each change tied to a failing test
- Avoid broad refactors until the regressions are green

**Step 2: Apply one measured performance improvement**

- Focus on repeated array/index construction, repeated scanning over columns, or expensive conversions in inner loops
- Keep behavior identical and prove it with tests

### Task 5: Verify Feasibility Before Claiming Success

**Files:**
- Test: `tests/test_binary.py`
- Test: `tests/test_straditizer.py`
- Test: other targeted tests changed in this work

**Step 1: Run focused regression tests**

Run: `pixi run python -m pytest tests/test_binary.py tests/test_straditizer.py -q`

**Step 2: Run any new regression tests**

Run: `pixi run python -m pytest tests/test_regressions.py -q`

**Step 3: Run a smoke import and startup check**

Run: `pixi run python -c "import straditize; from straditize.__main__ import get_parser; print(straditize.__version__); get_parser()"`

Expected: zero import errors and parser creation succeeds
