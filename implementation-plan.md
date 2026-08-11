# Implementation Plan – EPMCDMETST-59255

## Objective
Enhance the Employee Home page search to support a single multi-field query (Name or Employee ID or Phone or Department) and optional filters for Working Status and Department, while preserving current behavior when no criteria are provided.

Jira Story: EPMCDMETST-59255

## Scope
- Update listing logic in `emp_home` view to support:
  - Free-text query across `Emp.name`, `Emp.emp_id`, `Emp.phone`, `Emp.department` (case-insensitive, contains)
  - Working status filter: All / Active / Inactive
  - Department filter: select from existing department values in DB
- Update `templates/emp/home.html` to add filter controls and keep filter/query state in the UI after submit.
- Add tests for the new filtering behavior (unit tests for the view logic).

## Out of scope
- Adding new employee fields or changing the database schema
- Adding sorting, pagination, or advanced search (stemming, fuzzy, etc.)
- Add/Update form validation or UI redesign beyond minimal filter controls
- Delete confirmation flow or switching Delete to POST (tracked separately)

## Existing components (repo as found)
### Backend (Django)
- App: `emp`
  - Model: `emp.models.Emp`
  - Views: `emp.views`
  - URLs: `emp.urls` (included from `myapp/urls.py`)
- Templates: `templates/emp/home.html`

### Current behavior (baseline)
- Home page search parameter: `q` (GET)
  - Filters: only `name__icontains=q`
  - If no `q` all employees are shown
- Summary cards: total, active, inactive counts

## Impacted files
### Backend
- `emp/views.py` – update `emp_home` query/filter building

### Frontend
- `templates/emp/home.html` – add new filter inputs and update placeholder text

### Testing
- `emp/tests.py` – add unit/view tests for search + filters

## Frontend changes (detail)
### UI controls (GET layout)
Update the home page form to include these fields (all submitted as GET):
- Search input: `q` (existing)
  - Update placeholder from "Search by name" to "Search by name, employee ID, phone, or department"
- Working status filter: `status`
  - Allowed values: `all`, `active`, `inactive`
  - Default: `all` (when missing or invalid)
- Department filter: `department`
  - Dropdown options:
    - “All departments” (empty value or reserved value)
    - One option per distinct department value from existing employees
  - Must preserve selected option after submit using template logic.

### State preservation
- After search/filter submit, selected values remain in form controls.
- Employee table renders the filtered `emps` queryset.

## Backend changes (detail)
### Query parameters to support
Within `emp_home(request)` support:
- `q`: free-text, trimmed. If empty => treat as missing.
- `status`:
  - `all` => no filter on `working`
  - `active` => `working=True`
  - `inactive` => `working=False`
- `department`:
  - empty/missing => no department filter
  - non-empty => filter by department.

### Filtering logic
Dependency-ordered filtering:
1. Start with `Emp.objects.all()`.
2. Apply `q` filter using `django.db.models.Q`:
   - `Q(name__icontains=q) | Q(emp_id__icontains=q) | Q(phone__icontains=q) | Q(department__icontains=q)`
3. Apply working status filter based on `status`.
4. Apply department filter.

### Department dropdown data source
Provide distinct department values for rendering dropdown:
- Example: `Emp.objects.order_by('department').values_list('department', flat=True).distinct()`
- Exclude blank values if present.

### Counts cards (total/active/inactive)
Keep existing behavior:
- Total, active, inactive remain global counts (not filtered counts), since AC does not require filtered counts.

## Database impact
- None (read-only changes).

## Testing strategy
### Unit tests (Django)
Add view tests in `emp/tests.py` using Django `TestCase` + test client.

Test data: create 3–5 `Emp` objects spanning:
- Different departments (e.g., HR, IT)
- Both working statuses
- Distinct `emp_id` and `phone`

Test cases mapped to acceptance criteria:
1. Multi-field query:
   - Query matches by `name`
   - Query matches by `emp_id`
   - Query matches by `phone`
   - Query matches by `department`
2. Status filters:
   - `status=active` returns only `working=True`
   - `status=inactive` returns only `working=False`
   - `status=all` (and missing) returns both
3. Department filter:
   - `department=IT` returns only IT employees
4. Combined criteria:
   - `q=<...>&status=active&department=IT` behaves as intersection
5. No criteria:
   - No params => all employees

Assertions:
- HTTP 200
- Context `emps` contains expected employees (IDs)
- Context contains `q`, `status`, `department`, and `departments` (for dropdown)

### Manual smoke test
- Run server, open `/emp/home/`
- Verify dropdown renders and state preserves
- Verify search across all fields
- Verify combining filters
- Verify clearing filters shows all employees

## Risks
- Department values are free-text; case/spelling inconsistencies may fragment dropdown options (e.g., “IT” vs “It”).
- `icontains` queries can be slower at scale without indexes (acceptable for small app).

## Assumptions
- Server-rendered Django templates (no SPA).
- Department values are stored in `Emp.department` as non-null strings.
- Status filter values are controlled by UI; backend will handle unexpected values safely.

## Implementation sequence (dependency ordered)
1. Backend: update view logic (`emp/views.py`)
   - Import `Q`.
   - Parse `q`, `status`, `department`.
   - Build queryset with OR search + status + department.
   - Compute `departments` list.
   - Extend template context.
2. Frontend: update template (`templates/emp/home.html`)
   - Add `status` and `department` controls.
   - Preserve values after submit.
   - Update placeholder.
3. Tests (`emp/tests.py`)
   - Add `TestCase` coverage for AC 1–7.
4. Local validation
   - `python manage.py test`
   - Manual smoke test.

## Acceptance criteria traceability matrix
- AC1 (multi-field query) → `emp_home` Q-based OR filter; tests for each field.
- AC2/AC3 (Active/Inactive) → `status` mapping; tests.
- AC4 (All) → default and `status=all`; tests.
- AC5 (Department) → department filter + dropdown; tests.
- AC6 (Combine criteria) → sequential queryset filtering; combined test.
- AC7 (No criteria) → default `Emp.objects.all()`; test.
