# Implementation Plan – EPMCDMETST-59257

## Objective
Improve the home page employee search so that the existing single search input ("q" GET parameter) returns employees when the query matches any of these fields (contains, case-insensitive where applicable):

- name
- emp_id
- phone
- department

This must preserve current behavior when the search is left blank and must not affect add/update/delete flows.

Reference: Jira EPMCDMETST-59257

## Scope

### In scope
- Update the search logic in the home view (currently only `name__icontains`) to match against multiple fields using Django ORM.
- Keep the existing search input and GET pattern (`q` query param); maintain population of the input via template variable `q`.
- Add/update unit tests for the search behavior.

### Out of scope
- Any UI changes other than optional copy update to the placeholder text (the story doesn’t require it).
- Algorithmic/ranking search (fuzzy matching, scores, etc.).
- Add/Update/Delete flow changes or employee model schema changes.
- Any database index tuning or migrations.

## Existing components (repo observations)
- `emp/views.py`: contains `emp_home(request)` that currently reads `q` (GET) and filters `Emp` by `name__icontains` only.
- `emp/models.py`: defines model `Emp` with fields `name, emp_id, phone, department, address, working`.
- `templates/emp/home.html`: contains search form with input `name="q"` and displays `emps` table. Placeholder currently "Search by name".
- `emp/tests.py`: exists but currently empty.

## Impacted files
- `emp/views.py` – update search filter logic in `emp_home` to use multi-field OR filtering.
- `emp/tests.py` – add unit tests covering acceptance criteria.
- (Optional, only if approved) `templates/emp/home.html` – update search placeholder text to reflect multi-field search.

## Frontend changes
Requirements don’t require a UI change, beyond keeping the search term in the box (already handled by `value={{ q }}`).

Planned:
- No structural UI changes.
- Optional: change placeholder from "Search by name" to "Search by name, ID, phone, department". (Not part of AC; only do if accepted.)

## Backend changes

### Search logic (Django ORM) plan
1. Import `Q` object: `from django.db.models import Q` in `emp/views.py`.
2. In `emp_home`, keep the current pattern of reading and stripping `q`.
3. When `q` is non-empty, replace the single-field filter with an OR-combined Q object:

```py
emps = Emp.objects.filter(
    Q(name__icontains=q) |
    Q(emp_id__icontains=q) |
    Q(phone__icontains=q) |
    Q(department__icontains=q)
).distinct()
```

Notes:
- `emp_id` and `phone` appear to be stored as strings in the model; `__icontains` should work.
- `.distinct()` is a safe guard against duplication.
4. When `q` is empty, keep `emps = Emp.objects.all()` unchanged.
5. Keep summary counts (total/active/inactive) unmodified (AC doesn’t require these to be filtered by search).

## Database impact
- No database migrations or changes to the `Emp` model are required.
- No new indexes required for this scope.

## Testing strategy

### Unit tests (Django TestCase)
Add tests in `emp/tests.py`:
- Setup: create multiple employees with distinct values for `name`, `emp_id`, `phone`, `department`.
- Test: search by name returns expected employee(s).
- Test: search by emp_id returns expected employee.
- Test: search by phone returns expected employee.
- Test: search by department returns expected employee.
- Test: case-insensitivity (e.g., department "HR" matches query "hr").
- Test: empty query returns all employees.
- Test: search term persistence: response contains the `value="<query>"` in the rendered HTML and/or context `q` matches.

Assertions approach:
- Assert response status code 200.
- Assert `response.context['emps']` includes expected records.
- Assert length matches expected count.

### Manual smoke test
- Run server and verify the search box filters the table by each field; clearing query returns to all employees.

## Risks
- Performance: OR-based icontains on multiple fields can be slow on large datasets; likely acceptable for this app.
- Data type differences: if `emp_id` or `phone` are not text fields, `__icontains` may behave differently across DBs; tests should catch.
- Result duplication: low likelihood, but `.distinct()` mitigates.

## Assumptions
- Home page remains at `/emp/home/` (per existing redirects in views).
- Search input name stays `q` and the story does not require new filter controls.
- All four fields exist on the `Emp` model and are searchable via Django ORM.

## Implementation sequence (dependency-ordered)
1. Reconnaissance
   - Confirm `Emp` model field names and types in `emp/models.py`.
   - Confirm the home route in `emp/urls.py` maps to `emp_home` (needed for test client URL).
2. Backend: update search filter
   - Modify `emp/views.py`: import `Q` and update query logic to multi-field OR filter.
   - Ensure context variable `q` remains unchanged.
3. Tests
   - Implement unit tests in `emp/tests.py` to cover the acceptance criteria.
4. (Optional) Frontend copy
   - Update `templates/emp/home.html` placeholder text if agreed.
5. Verification
   - Run test suite; manually validate search behavior.
