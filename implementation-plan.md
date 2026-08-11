# Implementation Plan: Home page filters (Department & Working Status)

## Objective
Add filtering capabilities to the Employees home page so users can narrow the employee list by (1) Department and (2) Working Status (All/Active/Inactive), in combination with the existing name search.

## Inputs / Traceability
**Approved User Story:** “Home page: add filtering by Department and Working Status on the Home page”

**Acceptance Criteria (AC) to implement:**
1. Home page provides Department and Status filters in addition to name search.
2. Filters can be combined (e.g., name contains “Ann” + Department=IT + Status=Active).
3. Default state shows all employees when no filters are selected.
4. Results table reflects applied filters accurately.

## Scope
- Update the Home page UI to add two new filter controls:
  - Department dropdown (All + distinct departments)
  - Working Status dropdown (All / Active / Inactive)
- Update backend query logic in `emp_home` to apply these filters in combination with existing name search (`q`).
- Preserve existing dashboard metrics cards (Total/Active/Inactive) behavior (unfiltered, global counts), because AC does not request filtered metrics.

## Out of scope
- Normalizing/validating department values on add/update forms.
- Database schema changes or migrations.
- Pagination, sorting, or advanced search.
- New API endpoints (remain server-rendered).

## Existing components
- `emp/views.py::emp_home` currently reads `q` and returns `Emp.objects.filter(name__icontains=q)` or `Emp.objects.all()`.
- `templates/emp/home.html` contains a GET search form with a single input `q` and renders the employees table.
- Model `Emp` has fields `department` (text) and `working` (boolean).

## Impacted files
- Backend:
  - `emp/views.py`
- Frontend:
  - `templates/emp/home.html`
- Tests:
  - `emp/tests.py`

## Frontend changes
### Home page filter UI
- Extend the existing `<form method="GET">` to include:
  - `<select name="department">`:
    - option value "" => All
    - options from context variable `departments`
    - persist selection using `selected_department`
  - `<select name="status">`:
    - option value "" => All
    - option value `active` => Active
    - option value `inactive` => Inactive
    - persist selection using `selected_status`
- Keep the existing name search input `q` and button.
- Ensure the UX works on small screens (Bootstrap grid/flex).

## Backend changes
### Query parameters
- Read three GET params:
  - `q` (existing)
  - `department` (new)
  - `status` (new: allowed values `active|inactive|""`)

### Filtering logic (dependency-ordered)
1. Start with `emps = Emp.objects.all()`
2. If `q` is non-empty: `emps = emps.filter(name__icontains=q)`
3. If `department` is non-empty: `emps = emps.filter(department=department)`
4. If `status == "active"`: `emps = emps.filter(working=True)`
   If `status == "inactive"`: `emps = emps.filter(working=False)`
   Else: ignore status filter (treat as All)

### Department list for dropdown
- Provide `departments` in context as distinct non-empty department values from DB, e.g.
  - `Emp.objects.exclude(department__isnull=True).exclude(department__exact="").values_list("department", flat=True).distinct()`
  - optionally sort in Python

### Template context additions
- `departments`
- `selected_department`
- `selected_status`
- keep existing `q`, `emps`, and metrics.

## Database impact
None.

## Testing strategy
### Unit tests (Django TestCase)
Add tests in `emp/tests.py`:
1. Default: GET `/emp/home/` returns all employees.
2. Name-only search: `?q=ann` returns employees with matching names.
3. Department-only filter: `?department=IT` returns only IT employees.
4. Status-only filter:
   - `?status=active` returns only `working=True`
   - `?status=inactive` returns only `working=False`
5. Combined filters: `?q=ann&department=IT&status=active` returns correct intersection.
6. Invalid status value: `?status=foo` behaves like All (no error; returns unfiltered by working).

### Manual test checklist
- Verify dropdown values render and persist after submitting.
- Verify combinations work and URL is shareable.
- Verify metrics cards remain unchanged (global totals).

## Risks
- Department is free text; dropdown may show duplicates with different casing/spacing.
- Additional distinct query on every home page render (minor performance risk if dataset grows).

## Assumptions
- Home page route remains `/emp/home/` mapped to `emp_home`.
- Exact department match is acceptable because values come from dropdown.
- Jira key is not available in this workflow; branch name will be descriptive.

## Implementation sequence
1. Update `emp/views.py` to:
   - parse `department` and `status`
   - build filtered queryset
   - add `departments`, `selected_department`, `selected_status` to context
2. Update `templates/emp/home.html` to add dropdowns and persist selections.
3. Add/update tests in `emp/tests.py` to cover all AC.
4. Run test suite and manually validate UI.
