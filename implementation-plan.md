# Implementation Plan - EPMCDMETST-59160

## Objective
Implement server-side validation for the Employee Add and Update flows so that:
- Required fields are enforced: **Name, Employee ID, Phone, Department**.
- Phone must be **numeric and exactly 10 digits**.
- Employee ID must be **unique**.
- Validation errors are displayed clearly on Add/Update forms.
- Invalid data is **not saved**.
- Valid data is saved and user is redirected to **Employee Home**.

## Scope
In scope (traceable to Jira AC):
- Add validation for Add Employee (POST `/emp/add-emp/`).
  - Required: `emp_name`, `emp_id`, `emp_phone`, `emp_department`.
  - Phone: must match `^[0-9]{10}$`.
  - Uniqueness: `emp_id` must not already exist.
  - On validation failure: render same form with errors and prefilled values.
  - On success: save and redirect to `/emp/home/`.
- Add validation for Update Employee (POST `/emp/do-update-emp/<id>`).
  - Same required fields + phone rule.
  - Employee ID uniqueness across other rows (exclude current record).
  - On validation failure: re-render update form with errors and prefilled updated values.
  - On success: save and redirect to `/emp/home/`.
- Introduce a database-level unique constraint on `Emp.emp_id`.
  - Add Django migration.
- UI updates limited to displaying errors on `add_emp.html` and `update_emp.html`.
- Add tests covering validation scenarios for both Add and Update.

## Out of Scope
- Client-side (JS) validation, live validation, or input masking.
- UI redesign beyond error display.
- Additional validation rules (address format, allowed characters, phone country codes, etc.).
- Changing URL structure/endpoints.
- Normalizing Department into a separate table.

## Existing Components (as-is)
- Model: `emp/models.py` `class Emp`
  - fields: `name`, `emp_id`, `phone`, `address`, `working`, `department`
- Views: `emp/views.py`
  - `add_emp()` saves directly from POST without validation
  - `do_update_emp()` saves updates directly from POST without validation
- Templates:
  - `templates/emp/add_emp.html`
  - `templates/emp/update_emp.html`
- Tests: `emp/tests.py` exists but is currently a stub.

## Impacted Files
Backend / DB:
- `emp/models.py`
- `emp/migrations/0002_<...>_emp_emp_id_unique.py` (new)
- `emp/views.py`
- `emp/tests.py`

Frontend:
- `templates/emp/add_emp.html`
- `templates/emp/update_emp.html`

## Frontend Changes (Templates)
- Add a visible validation error section at top of each form (Bootstrap `alert alert-danger`).
- Display field-level errors near the relevant inputs (or clearly list them grouped by field).
- Preserve user-entered values on validation failure:
  - Add form: show posted values back in inputs/textarea/select.
  - Update form: prefer posted values when re-rendering after failed POST; otherwise use existing `emp` values.
- Ensure department `<select>` reflects current/posted value by adding `selected` attribute on matching `<option>`.

## Backend Changes
### Validation approach
Add a helper (either in `emp/views.py` or a new `emp/validation.py`) to validate and normalize request POST data.

Validation rules:
- `emp_name`: required, non-empty after `strip()`.
- `emp_id`: required, non-empty after `strip()`; must be unique.
- `emp_phone`: required; must be all digits and length exactly 10.
- `emp_department`: required (non-empty).

Uniqueness checks:
- On Add: `Emp.objects.filter(emp_id=emp_id).exists()`
- On Update: `Emp.objects.exclude(pk=<current_pk>).filter(emp_id=emp_id).exists()`

Error handling:
- If validation errors exist: do **not** call `save()`.
- Return `render()` with `errors` and `form_values` in context.
- As a safety net, catch `django.db.IntegrityError` around `save()` (in case of race conditions or DB constraint violations) and convert into a friendly `emp_id` uniqueness error.

### View-specific changes
- `add_emp(request)`:
  - On POST: validate; if OK create Emp and save; redirect to `/emp/home/`.
  - On errors: render `emp/add_emp.html` with context.
- `do_update_emp(request, emp_id)`:
  - On POST: validate; if OK update fields and save; redirect to `/emp/home/`.
  - On errors: re-render `emp/update_emp.html` with context including the `emp` object and posted values.

## Database Impact
- Add unique constraint on `Emp.emp_id`.
- Django migration required.

Migration risk note:
- Migration will fail if the existing database contains duplicate `emp_id` values.
- Since `db.sqlite3` is checked into the repo, confirm and clean duplicates in development DB before applying the migration (or update the checked-in DB accordingly) while keeping production code unchanged.

## Testing Strategy
### Automated tests (Django TestCase)
Add tests in `emp/tests.py` using Django test client:

1) Add Employee - required fields
- POST missing name/emp_id/phone/department => response 200, error messages present, Emp count unchanged.

2) Add Employee - phone format
- POST phone with letters or <10 or >10 digits => not saved, phone error shown.

3) Add Employee - unique emp_id
- Create an Emp with emp_id="E001" then POST another with same emp_id => not saved, uniqueness error shown.

4) Add Employee - success
- Valid POST => redirect (302) to `/emp/home/`, record exists.

5) Update Employee - unique emp_id excluding self
- Two employees A(emp_id=E001) and B(emp_id=E002). Update B with emp_id=E001 => not saved, error shown.

6) Update Employee - success
- Update employee with valid changes => redirect and persisted.

### Manual verification
- Open Add form, submit empty => see clear errors.
- Submit invalid phone => see phone error.
- Submit duplicate ID => see uniqueness error.
- Submit valid => redirected to Home.
- Repeat on Update flow.

## Risks
- Existing checked-in SQLite DB may contain duplicates, blocking migration.
- Unhandled IntegrityError on save if uniqueness enforced at DB level without try/except.
- Template select not reflecting existing department value (currently `select value="{{emp.department}}"` does not set selected option).

## Assumptions
- Only server-side validation is required (per story).
- Department dropdown values (`CSE`, `ME`, `EE`) remain as-is; department is considered required because it is part of the form.
- `emp_id` is a business identifier but primary key remains Django `id`.
- Redirect target remains `/emp/home/`.

## Implementation Sequence (dependency-ordered)
1) **Create validation helper**
   - Decide location (`emp/views.py` helper or new `emp/validation.py`).
   - Implement validation rules and uniqueness checks.

2) **Update Add/Update views**
   - Modify `add_emp` and `do_update_emp` to call validation.
   - Ensure no `save()` happens on invalid data.
   - Add IntegrityError safety net.

3) **Update templates to show errors & preserve input**
   - Add error sections.
   - Populate fields from posted values on failures.
   - Fix department select to correctly mark selected option.

4) **Database migration**
   - Update `Emp` model with unique constraint for `emp_id`.
   - Generate and add migration.
   - Confirm migration applies cleanly (resolve duplicates in dev DB if needed).

5) **Add automated tests**
   - Implement test cases mapped to acceptance criteria.

6) **Final verification**
   - Run test suite.
   - Manually verify form behaviors.
