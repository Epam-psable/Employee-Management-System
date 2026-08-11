# Implementation Plan – EPMCDMETST-59279

## Jira User Story

- **Key**: EPMCDMETST-59279
- **Summary**: Expand employee search to include Employee ID and Department
- **Acceptance Criteria**:
  1) When a user searches using query parameter `q`, results include employees where `q` matches any of:
     - `name` (contains, case-insensitive)
     - `emp_id` (contains, case-insensitive)
     - `department` (contains, case-insensitive)
  2) When `q` is empty, all employees are shown (current behavior preserved).

- **Screens/Pages Impacted**: Employee Home page (`/emp/home/`)

---

## Objective

Improve employee search so that the existing search box (`q` query parameter) returns employees matching by **Name or Employee ID or Department**, using case-insensitive **contains** matching. Preserve current behavior when the query is omitted or empty.

## Scope

### In scope

- Update the backend query logic in `emp/views.py:emp_home` to filter `Emp` by name/emp_id/department when `q` is present and non-empty.
- Ensure search is case-insensitive and uses substring match (`__icontains`) across all three fields.
- (Optional but recommended) Update search placeholder text on the home page to reflect the new search capability (e.g., "Search by name, ID, or department").
- Add unit tests for the updated search behavior (including empty-query behavior).

### Out of scope

- Adding new UI controls (advanced filters, dropdowns, typeahead).
- Changing the existing URL or routing structure.
- Adding new database indexes or migrations (not required by AC).
- Any modification to employee create/update/delete flows.

---

## Existing components (repo analysis)

### Backend (Django)

- App: `emp` (employee management)
- Model: `emp/models.py:Emp` with fields:
  - `name` (CharField)
  - `emp_id` (CharField)
  - `phone` (CharField)
  - `address` (CharField)
  - `working` (BooleanField)
  - `department` (CharField)
- View: `emp/views.py:emp_home` currently supports search by `name__icontains` only.
- Template: `templates/emp/home.html` contains a single search input named `q` with placeholder "Search by name".

### Frontend

- Server-rendered HTML (Django templates) + Bootstrap CDN.
- Search is triggered via GET form submit on the home page.

---

## Impacted files

**Backend**
- `emp/views.py`

**Frontend/Templates**
- `templates/emp/home.html` (optional placeholder update)

**Tests**
- `emp/tests.py`

**Docs (optional)**
- `README.md`

---

## Frontend changes

- `templates/emp/home.html`
  - Update the search input placeholder from **"Search by name"** to **"Search by name, ID, or department"**.
  - No change to:
    - `method="GET"`
    - input `name="q"`
    - binding `value="{{ q|default:'' }}"`

---

## Backend changes

- `emp/views.py` (`emp_home`)
  - Keep: `q = request.GET.get("q", "").strip()`
  - When `q` is non-empty:
    - Import `Q` from `django.db.models`.
    - Filter with OR conditions:
      - `name__icontains=q`
      - `emp_id__icontains=q`
      - `department__icontains=q`
    - Add `.distinct()` to prevent duplicate rows when multiple fields match the same employee.
  - When `q` is empty:
    - Preserve behavior: return all employees (`Emp.objects.all()`).
  - KPI counts (total/active/inactive) remain global counts (as currently implemented).

---

## Database impact

- **No schema changes** required.
- Query will now touch additional columns (`emp_id`, `department`).
- Non-blocking note: if the employee table grows significantly, adding indexes could be considered in a future performance story.

---

## Testing strategy

### Unit tests (Django `TestCase`)

Add tests in `emp/tests.py`:

1. **Search by name**
   - Given employees exist, when requesting `/emp/home/?q=<name-fragment>` results include matching employee(s).

2. **Search by employee ID**
   - When requesting `/emp/home/?q=<id-fragment>` results include matching employee(s).

3. **Search by department**
   - When requesting `/emp/home/?q=<department-fragment>` results include matching employee(s).

4. **Case-insensitivity**
   - Mixed-case `q` returns the same as lower-case.

5. **Empty query shows all**
   - No `q` param or `q=` returns all employees.

Assertions:
- Prefer asserting count and membership over strict ordering.

### Manual smoke checks

- Run `python manage.py runserver`
- Visit `/emp/home/` and try searching by:
  - partial name
  - partial employee ID
  - department fragment
- Clear search and confirm all employees return.

---

## Risks

- **Performance**: OR queries across multiple `__icontains` filters can be slower on large datasets.
- **Duplicates**: Without `.distinct()`, the same employee could appear multiple times if multiple fields match.
- **Test fragility**: Tests must not depend on default ordering unless explicitly set.

---

## Assumptions

- The home page remains the employee listing and search endpoint.
- The query parameter remains named `q` and search continues to be GET-based.
- Model fields remain `name`, `emp_id`, `department`.

---

## Implementation sequence (dependency-ordered)

1. **Confirm current behavior**
   - Review `emp/views.py:emp_home` and `templates/emp/home.html` search form.

2. **Backend query update**
   - Add `Q` import.
   - Implement OR filtering for `name`, `emp_id`, and `department` with `.distinct()`.
   - Ensure empty query path still returns all employees.

3. **Frontend copy update (optional)**
   - Update placeholder to reflect expanded search.

4. **Add/Update tests**
   - Create employees in test setup.
   - Write tests for name/id/department search + empty query.

5. **Regression check**
   - Ensure KPIs still display.
   - Ensure CRUD navigation/actions remain unchanged.
