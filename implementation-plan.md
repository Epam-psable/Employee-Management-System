# Implementation Plan - EPMCDMETST-59268

## Jira User Story (reference)
- **Key**: EPMCDMETST-59268
- **Summary**: Prevent duplicate Employee ID on create/update with user-friendly validation message
- **Priority**: Medium
- **Acceptance Criteria**:
  1. Given an existing employee with emp_id = X, when a user attempts to create a new employee with emp_id = X, then the employee is not saved and the UI shows a clear validation error.
  2. Given an existing employee with emp_id = X, when a user edits another employee and sets emp_id = X, then the update is blocked with a validation error.
  3. Existing valid records continue to display and function normally.

## Objective
Ensure employee records have a **unique** `emp_id` across create and update, and provide a clear, user-friendly validation error in the UI when a duplicate is attempted.

- Data-level protection: add a database uniqueness constraint for `Emp.emp_id`.
- App-level UX: detect duplicates on form submission (add/update) and re-render the form with an error instead of redirecting.

---

## Scope
In scope:
1. Enforce unique constraint on `Emp.emp_id` (model + migration).
2. Update create (`add_emp`) and update (`do_update_emp`) logic to prevent saving duplicates and return a validation error.
3. Update add/update templates to show the error message.
4. Add tests covering duplicate `emp_id` on create and update.

## Out of scope
- Any redesign of UI beyond adding error messaging.
- Expanding search or other enhancements.
- Additional validation (phone format, required fields beyond what is needed for this story).
- Automated deduplication/cleanup of existing duplicate data beyond the prerequisite step to make migrations succeed.
- Admin site improvements.

---

## Existing components (repo observations)
- **Model**: `Emp` in `emp/models.py` with fields: `name`, `emp_id`, `phone`, `address`, `working`, `department`. Currently `emp_id` is not unique.
- **Views** (`emp/views.py`):
  - `add_emp`: reads POST values, creates `Emp`, calls `save()`, then redirects.
  - `do_update_emp`: loads an `Emp` by pk, updates fields, calls `save()`, then redirects.
  - No Django Forms are used; validation must be handled manually.
- **Templates**:
  - `templates/emp/add_emp.html`
  - `templates/emp/update_emp.html`
  - No existing error placeholders.

---

## Impacted files
Expected direct changes:
- `emp/models.py` — add uniqueness constraint for `emp_id`.
- `emp/migrations/*` — new migration to add unique constraint/index.
- `emp/views.py` — add duplicate checks + IntegrityError handling; return render with error.
- `templates/emp/add_emp.html` — render error (and optionally repopulate fields).
- `templates/emp/update_emp.html` — render error (and optionally repopulate fields).
- `emp/tests.py` — add tests.

---

## Frontend changes
Because the app uses manual HTML forms (not Django Forms), error feedback must be passed via view context.

### `templates/emp/add_emp.html`
- Add an error container (e.g., Bootstrap alert) rendered when `error` exists in context.
- Repopulate form values on error using context variables (e.g., `emp_name`, `emp_id`, etc.) so the user doesn’t lose input.
- Recommended error copy: "Employee ID already exists. Please use a different ID." (must be clear; exact wording can vary).

### `templates/emp/update_emp.html`
- Add similar error container.
- Ensure displayed values reflect the user’s attempted changes when re-rendering after validation failure.
  - Option A: pass a separate `form` dict in context and use those values in template.
  - Option B: pass `emp` plus override variables.

---

## Backend changes

### 1) Model-level uniqueness
In `emp/models.py`, enforce uniqueness using one of:
- `emp_id = models.CharField(max_length=200, unique=True)`
- or `UniqueConstraint(fields=['emp_id'], name='unique_emp_emp_id')` in `Meta.constraints`.

Also consider trimming user input (`.strip()`) in views before validating/saving to avoid duplicates caused by whitespace.

### 2) View-level validation & error handling
In `emp/views.py`:

#### `add_emp`
- Strip `emp_id`.
- Pre-check:
  - `if Emp.objects.filter(emp_id=emp_id).exists():` then render `emp/add_emp.html` with `error` and repopulation values.
- Save only if unique.
- Add a DB backstop:
  - wrap `e.save()` in try/except for `django.db.IntegrityError` to catch race conditions and render the same friendly error.

#### `do_update_emp`
- Strip the submitted `emp_id`.
- Pre-check duplicates excluding current record:
  - `if Emp.objects.filter(emp_id=emp_id_temp).exclude(pk=emp_id).exists():` then render `emp/update_emp.html` with `error` and attempted values.
- Otherwise save; similarly wrap `save()` in try/except `IntegrityError`.

---

## Database impact
- A unique index/constraint will be added for `emp_id`.
- Migration will fail if the existing database contains duplicates.

### Pre-migration operational step
Before applying migration in any environment with existing data, run a check for duplicates and resolve them:
```py
from emp.models import Emp
from django.db.models import Count

dupes = (Emp.objects.values('emp_id')
         .annotate(c=Count('id'))
         .filter(c__gt=1))
print(list(dupes))
```
Resolve duplicates manually (e.g., update `emp_id` values) so the migration can apply.

---

## Testing strategy
Add Django unit tests in `emp/tests.py`.

1. **Create duplicate blocked**
- Create an employee with `emp_id='E123'`.
- POST to `/emp/add-emp/` with the same `emp_id`.
- Assert:
  - response status is 200 (form re-rendered) and contains error message
  - employee count does not increase

2. **Update duplicate blocked**
- Create employee A with `emp_id='E123'` and employee B with `emp_id='E456'`.
- POST update for B with `emp_id='E123'`.
- Assert:
  - response status is 200 and contains error
  - B’s `emp_id` remains unchanged in DB

3. **DB constraint backstop** (optional but recommended)
- Attempt to create two `Emp` objects with same `emp_id` and assert `IntegrityError`.

---

## Risks
- **Migration failure** if duplicates exist in current DB.
  - Mitigation: run the duplicate check and fix data before applying migration.
- **Race condition** between pre-check and save.
  - Mitigation: DB unique constraint + `IntegrityError` handling.
- **User input normalization ambiguity** (case-sensitivity, whitespace).
  - Assumption: exact-match uniqueness; we will trim whitespace but not enforce case-insensitive uniqueness unless required.

---

## Assumptions
- Requirements are limited to preventing duplicates and showing a clear UI error.
- The app remains function-based with manual form parsing (no refactor to Django Forms in this story).
- Default branch is `main`.

---

## Implementation sequence (dependency-ordered)
1. Review current model/view/template flows for employee creation and update.
2. Identify and resolve any existing duplicate `emp_id` data in target DB(s) (operational prerequisite).
3. Update `emp/models.py` to enforce `emp_id` uniqueness.
4. Generate and commit migration in `emp/migrations/`.
5. Update `emp/views.py` to:
   - strip and validate `emp_id` uniqueness on create/update
   - render templates with clear error on duplicates
   - catch `IntegrityError` and show same message
6. Update templates to display `error` and repopulate entered values on validation failure.
7. Add/extend tests in `emp/tests.py` for create and update duplicate scenarios.
8. Run test suite and perform basic manual verification in the UI.
