# Implementation Plan: Server-side validation and inline errors for Employee Add/Update forms

## Objective
Add server-side validation and inline error feedback for the **Add Employee** and **Update Employee** forms to ensure data quality and prevent invalid/partial persistence.

Validation rules (as specified in the approved story):
- Name required
- Employee ID (emp_id) required
- Phone must be exactly 10 digits (0-9)
- Employee ID must be unique (on create and update, excluding the current record during update)
- Validation errors displayed inline
- When validation fails, the form remains populated with user-entered values
- Invalid data must not be saved

## Scope
**In scope**
1. Server-side validation in the add and update flows:
   - Required: name, emp_id
   - Phone: exactly 10 digits
   - Uniqueness: emp_id must be unique
     - Add: backend checks for any existing Emp with emp_id
     - Update: backend checks for any other Emp with same emp_id
   - No save() call when validation fails
2. Template changes to show field-level errors inline and preserve values on re-render.
3. Light refactor to centralize validation logic to avoid duplication between add and update (stay within existing function-based views; do not introduce a new architecture by default)

## Out of scope
- Client-side JS validation (e.g., input masks)
- Authentication/authorization
- Changing urls, routes, or adding new pages
- Any change to delete flow (still GET-based currently)
- DB schema migrations beyond what is required to enforce uniqueness (see Database impact section for options)

## Existing components (repo observations)
- **Model**: `emp/models.py` has `Emp` model with fields `name, emp_id, phone, address, working, department`.
  - `emp_id` currently not unique at the DB schema level.
  - `phone` currently has max_length=10 but no validation ensures all chars are digits and length is exactly 10.
- **Views**: `emp/views.py`
  - `add_emp` reads POST fields and persists without validation.
  - `do_update_emp` updates an employee and saves without validation.
- **Templates**:
  - `templates/emp/add_emp.html`: form has no value binding and no error display.
  - `templates/emp/update_emp.html`: prepopulates via `{{emp.field}}`, but no error display.

## Impacted files
Expected to be modified by the developer during implementation (no code changes in this workflow):
- `emp/views.py` — add validation logic and re-render on error
- `templates/emp/add_emp.html` — display inline errors and preserve values
- `templates/emp/update_emp.html` — display inline errors and preserve values
- `emp/models.py` — (optional/recommended) enforce uniqueness at DB schema level (add `unique=True`)
- `emp/migrations/0002_*.py` — (optional/recommended if model changes) migration to add unique constraint
- `emp/tests.py` — add unit/view tests for validation rules

## Frontend changes (templates)
**Goal**: Show field-level errors next to the relevant input, and preserve user entries when the form is re-rendered due to validation failure.

Proposed template pattern (without introducing Django Forms):
- Pass `form_values` dict (or individual variables like `emp_name`, `emp_id`, etc.) from views to template.
  - On GET: values may be empty (add) or from `emp` (update)
  - On POST with errors: values come from `request.POST` to keep user input
- Pass an `errors` dict mapping field -> error text.
- Use Bootstrap invalid feedback patterns: add `is-invalid` class and render `<div class="invalid-feedback">...</div>`.

Template-level tasks (`add_emp.html`):
- Add `value="{{ form_values.emp_name|default:'' }}"` on name/id/phone inputs.
- For `<textarea>`, render `{{ form_values.emp_address|default:'' }}` inside textarea.
- For `<select>`, apply `selected` based on submitted department.
- For checkbox, set checked based on submitted working status.
- Show errors under each field if present in `errors`.

Template-level tasks (`update_emp.html`):
- Same pattern; on validation error, use posted values overriding `{{emp.field}}`.
- Fix current bug: `select value="{{emp.department}}"` does not set selection in HTML; must use `selected` on `<option>`.

## Backend changes (Django views)
**Goal**: Validate in POST handlers; on failure re-render same template with errors and input values; on success persist and redirect as today.

### 1) Add a reusable validation helper
Create (conceptually) a helper in `emp/views.py` or a new module (e.g., `emp/validation.py`):
- Input: dict-like data (`request.POST`), and optionally `current_emp_pk` (or `Emp` instance) when updating.
- Output: `(cleaned_data, errors)`
  - `errors` is a dict: `{ "emp_name": "message", "emp_id": "message", "emp_phone": "message" }`

Validation details (traceable to AC):
- Name: `strip()`; if empty -> "Name is required."
- Employee ID: `strip()`; if empty -> "Employee ID is required."
  - Uniqueness: `Emp.objects.filter(emp_id=emp_id)`
    - Add: if exists -> "Employee ID must be unique."
    - Update: exclude current record by pk; if another exists -> same message
- Phone: allow only digits and length exactly 10
  - If phone has any non-digit or length != 10 -> "Phone must contain exactly 10 digits."

### 2) Wire validation into `add_emp`
Planned flow:
- On POST, run validation helper.
  - If errors: render `emp/add_emp.html` with `{errors, form_values}` and **do not call save()**.
  - If ok: create Emp, set fields, save, redirect `/emp/home/`.

### 3) Wire validation into `do_update_emp`
Planned flow:
- On POST, load existing `Emp` by pk.
- Validate posted values with helper, passing current pk to exclude from uniqueness check.
  - If errors: render `emp/update_emp.html` with `{emp, errors, form_values}` and **do not call save()**.
  - If ok: apply updates, save, redirect `/emp/home/`.

Note: `update_emp` GET handler can remain, but template must support both initial and error re-render contexts.

## Database impact
**Minimum required**: None. The story requires uniqueness validation which can be enforced at the application layer.

**Recommended hardening (still aligned to AC)**: Add a DB unique constraint on `emp_id`.
- Change `emp/models.py`: `emp_id = models.CharField(max_length=200, unique=True)`
- Generate migration (e.g., `0002_alter_emp_emp_id_unique.py`)
- Risk: if existing data already has duplicates, migration will fail. Plan a pre-check/cleanup step before enabling the constraint in production.
- If DB constraint is added, catch `IntegrityError` on save and re-render with the same inline error message for emp_id.

## Testing strategy
**Unit and View-level tests (Django TestCase)** in `emp/tests.py`:
- Add Employee - missing name: expect 200, error text present, and `Emp.objects.count()` unchanged.
- Add Employee - missing emp_id: same.
- Add Employee - phone non-digits or wrong length: 200, inline error, no save.
- Add Employee - duplicate emp_id: pre-create Emp with emp_id="X", POST another with same emp_id; expect validation error.
- Update Employee - set emp_id to another employee’s emp_id: error, and employee not updated.
- Value persistence on error: assert response contains submitted values in rendered HTML.

Manual testing checklist:
- Add with empty name -> inline error, values preserved.
- Add with phone="1234" -> error, no record created.
- Add with duplicate emp_id -> error.
- Update to duplicate emp_id -> error, record unchanged.
- Success cases still redirect to home and data is saved.

## Risks
1. **DB migration failure if adding unique constraint**: existing rows may have duplicate emp_id.
   - Mitigation: run audit query before migration; clean duplicates; or enforce uniqueness at app-level only.
2. **False positives on phone validation**: users may enter formatted numbers ("123-456-7890").
   - Mitigation: story requires exactly 10 digits; keep rule strict and error message clear.
3. **Race condition for uniqueness without DB constraint**: two requests could pass check and save duplicates.
   - Mitigation: add DB constraint if possible; otherwise handle at application level only.

## Assumptions
1. Jira story key is not available in this workflow (no Jira key returned), so the feature branch uses a `NO-JIRA` prefix.
2. The project remains function-based views + templates; no switch to Django Forms unless explicitly approved.
3. Department options remain static as currently defined in templates.

## Implementation sequence (dependency-ordered)
1. Identify current add/update form field names and mapping.
2. Implement validation helper returning `errors` + cleaned values.
3. Integrate helper into `add_emp` (re-render with errors + preserve values on failure).
4. Integrate helper into `do_update_emp` (exclude current pk in uniqueness check; re-render on failure).
5. Update templates to:
   - bind values from context
   - render inline errors using Bootstrap invalid feedback
   - ensure department select shows correct selected option
6. (Optional) Add DB unique constraint on `emp_id` + migration + catch `IntegrityError`.
7. Add automated tests covering each acceptance criterion.

## Traceability matrix (AC -> plan steps)
- AC: Name required -> Steps 2-4, 7
- AC: Employee ID required -> Steps 2-4, 7
- AC: Phone exactly 10 digits -> Steps 2-4, 7
- AC: Employee ID unique (create/update) -> Steps 2-4, (optional 6), 7
- AC: Values remain populated on validation failure -> Step 5, 7
- AC: Invalid data not saved -> Steps 3-4, 7
