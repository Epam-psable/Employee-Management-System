# UI E2E Tests (Pytest + Playwright)

## Install
```bash
pip install -r requirements-test.txt
playwright install
```

## Run
```bash
pytest -q
```

## Notes
- Tests start Django `runserver` on `http://127.0.0.1:8001`.
- Tests use an isolated SQLite DB file via env var `EMS_UI_TEST_DB` (supported in `myapp/settings.py`).
- Each test seeds deterministic employees.

## Known Gaps (Expected Failures)
Some tests are marked `xfail` to document current gaps:
- Invalid delete id returns 500 (should be handled gracefully)
- Department dropdown is not preselected on update form
