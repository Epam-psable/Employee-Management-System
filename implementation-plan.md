# Implementation Plan - EPMCDMETST-59261

## Jira User Story
- **Key**: EPMCDMETST-59261
- **Summary**: Enforce unique Employee ID and validate phone number on employee create/update
- **Acceptance Criteria**:
  1. Creating an employee with an emp_id that already exists is rejected with a clear message.
  2. Phone field rejects non-numeric input and invalid length (10 digits) with a clear message.
  3. Update flow enforces the same emp_id uniqueness and phone validation rules.
  4. Valid submissions for create/update continue to work as-is.

## Objective
Improve data integrity and user feedback by enforcing uniqueness of employee identifiers (`emp_id`) and enforcing a strict phone format (10 digits, numeric) during employee create and update, with clear validation messages shown to the user.

## Scope
In scope:
- Add a DB-level uniqueness constraint for `Emp.emp_id`.
- Add server-side validation for:
  - `emp_id`: required (non-blank) and unique.
  - `phone`: exactly 10 digits and numeric.
- Apply validation consistently for both create (`add_emp`) and update (`do_update_emp`).
- Update templates to display validation errors and preserve user input when re-rendering after validation failure.
- Add automated tests covering validation and uniqueness behavior.

Out of scope:
- UI redesign beyond adding error message display.
- Changing phone format rules beyond “10 numeric digits”.
- Bulk cleanup of existing duplicate `emp_id` values (migration will fail until fixed; see Risks).
- Any other enhancements (delete confirmation, filtering, etc.).

## Existing components (repository analysis)
- `emp/models.py`: Django model `Emp` with fields: `name`, `emp_id`, `phone`, `address`, `working`, `department`.
- `emp/views.py`: Function-based views manually reading POST parameters and saving models.
  - Create: `add_emp`
  - Update: `update_emp` (GET form) + `do_update_emp` (POST submit)
- Templates:
  - `templates/emp/add_emp.html`: add form.
  - `templates/emp/update_emp.html`: update form.
- Database: SQLite (`db.sqlite3`) tracked in repo.

## Impacted files
Backend:
- `emp/models.py`
- `emp/views.py`
- `emp/tests.py`
- `emp/migrations/000X_*.py` (new migration to add uniqueness constraint)
- (Optional) `emp/forms.py` (recommended approach)

Frontend:
- `templates/emp/add_emp.html`
- `templates/emp/update_emp.html`

## Frontend changes
- Add placeholders for validation feedback near Employee ID and Phone fields.
- Preserve submitted values when re-rendering the page after validation failure.
- Recommended approach:
  - If moving to Django Forms: render `form` errors (`{{ form.emp_id.errors }}`, `{{ form.phone.errors }}`) and bind `value` attributes using form widgets.
  - If staying with manual POST parsing: pass `errors` + `form_data` dict to template and render them.

## Backend changes
### Recommended approach: Introduce Django ModelForm
Reason: centralized validation, consistent error handling, less duplicated code.

1) Create `emp/forms.py`:
- `EmpForm(forms.ModelForm)`
  - `Meta.model = Emp`
  - `fields = ['name','emp_id','phone','address','working','department']`
  - `clean_phone`: enforce regex `^\d{10}$` and raise `ValidationError('Phone number must be exactly 10 digits.')`
  - `clean_emp_id`: strip whitespace and ensure uniqueness:
    - For create: `Emp.objects.filter(emp_id=val).exists()`
    - For update: exclude the current instance: `Emp.objects.exclude(pk=self.instance.pk).filter(emp_id=val).exists()`
    - Raise `ValidationError('Employee ID already exists. Please use a different ID.')`

2) Update `emp/views.py`:
- `add_emp`:
  - GET: `form = EmpForm()`
  - POST: `form = EmpForm(request.POST)`
    - if valid: `form.save()` then redirect `/emp/home/`
    - else: render `emp/add_emp.html` with `form` (status 200)
- `do_update_emp`:
  - Load instance by pk.
  - POST: `form = EmpForm(request.POST, instance=emp)`
    - if valid: save and redirect
    - else: render `emp/update_emp.html` with `form` and `emp`
- Keep `update_emp` GET view:
  - Use `form = EmpForm(instance=emp)` and render.
- Add defensive handling for DB uniqueness race:
  - Catch `django.db.utils.IntegrityError` during save and attach a form error on `emp_id`.

### Alternative (minimal change): Keep manual parsing
- Add duplicate check and phone validation before `.save()` and re-render templates with errors.
- Still add model uniqueness constraint to prevent race conditions.

## Database impact
- Add uniqueness constraint/index for `Emp.emp_id`.
- Migration will fail if existing records contain duplicate `emp_id` values.
- Developer must verify/clean local DB before applying migrations.

## Testing strategy
Add tests in `emp/tests.py`:
1) Phone validation:
- Reject non-numeric (`'12345abcde'`)
- Reject length != 10 (`'123'`, `'12345678901'`)
- Accept 10 digits (`'0123456789'`)
2) emp_id uniqueness:
- Create emp with emp_id 'E1'
- Attempt create another with emp_id 'E1' => response 200 and error message present
- Update same employee with unchanged emp_id => allowed
- Update employee to another existing emp_id => blocked with error

Test level:
- Prefer client POST integration tests against endpoints `/emp/add-emp/` and `/emp/do-update-emp/<id>/`.

## Risks
- Existing DB duplicates of `emp_id` will break migration.
- Manual templates may not be compatible with switching to Django Forms without small refactor.
- Race conditions: concurrent creates may still hit DB constraint; must handle IntegrityError gracefully.

## Assumptions
- Phone format requirement is exactly 10 numeric digits (per AC).
- `emp_id` uniqueness is global across all employees.
- It is acceptable to add a migration in the repo.

## Implementation sequence (dependency ordered)
1) Repository pre-check:
- Inspect existing data in `db.sqlite3` for duplicate `emp_id` values (document how to detect).
2) Model change:
- Update `Emp.emp_id` to be unique (or add `UniqueConstraint` in `Meta`).
3) Generate migration:
- Create and apply migration locally.
4) Validation layer:
- Add `EmpForm` with `clean_phone` and `clean_emp_id`.
5) Update views:
- Refactor create/update flows to use the form; ensure validation errors re-render the same page.
- Add IntegrityError handling.
6) Update templates:
- Display `form` fields and errors (or map to existing inputs if keeping structure).
7) Tests:
- Add unit/integration tests for AC scenarios.
8) Manual verification:
- Validate create/update success paths still redirect to `/emp/home/`.
