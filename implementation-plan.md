# Implementation Plan – EPMCDMETST-59264

## Objective
Expand the existing employee search on the Home (`emp_home`) page so that the existing query parameter `q` matches across (partial, case-insensitive):
- Employee Name (existing behavior)
- Employee ID (`Emp.emp_id`)
- Department (`Emp.department`)

This story must not require any UI changes and must continue to use the existing `q` query string.

**Traceability to Jira AC:** Filter results for match by `emp_id`, `department`, and behave as today for `name`.

---

## Scope
In scope:
- Backend change in the home list view to update the query to search across multiple fields.
- Add unit tests for the new search behavior (name/emp_id/department).
- Document the search behavior in README if the repo has a usage section (optional).

Out of scope:
- Any change to the user interface (search box, labels, new filter controls).
- Advanced search (multiple query terms, quoted groups, regex), sorting, pagination.
- Database model/schema changes.
- Performance optimizations beyond basic good practice (e.g., adding indexes).

---

## Existing components (from repo analysis)
- Django app: `emp`
- Templates: server-rendered templates in `templates/emp/`
- Home view: `emp/views.py::emp_home`
  - Currently: if `q`: `Emp.objects.filter(name__icontains=q)`
- Model: `emp/models.py::Emp`
  - Fields relevant: `name`, `emp_id`, `department`

---

## Impacted files
Backend:
- `emp/views.py` – update search query logic to OR across multiple fields using `Q`.

Frontend (verification only, likely no change):
- `templates/emp/home.html` – confirm it still submits `q` and displays results.

Testing:
- `emp/tests.py` – add tests for searching by name, employee id, department, and empty query.

Docs (optional):
- `README.md` – note that `q` matches name/emp_id/department.

---

## Frontend changes
No planned UI changes.

Verification only:
- Confirm the search input is wired to the query string parameter `q`.
- Confirm the value of `q` is displayed/retained (context already passes `q`).

---

## Backend changes
### Current behavior
```py
q = request.GET.get("q", "").strip()
if q:
    emps = Emp.objects.filter(name__icontains=q)
else:
    emps = Emp.objects.all()
```

### Target behavior
Use an OR-combined queryset so `q` matches name OR employee id OR department:

```py
from django.db.models import Q

q = request.GET.get("q", "").strip()
if q:
    emps = Emp.objects.filter(
        Q(name__icontains=q) |
        Q(emp_id__icontains=q) |
        Q(department__icontains=q)
    )
else:
    emps = Emp.objects.all()
```

Notes:
- Keep summary counts unchanged (they are currently computed across all employees, not filtered).
- Consider `.distinct()` only if future joins could produce duplicates (not required now).

---

## Database impact
No schema changes.

Performance:
- This is a case-insensitive contains query across three columns. For typical small datasets, acceptable.

---

## Testing strategy
Add/extend tests using Django’s `TestCase` + test client in `emp/tests.py`.

### Test data
Create 3 employees with distinct values:
- Emp A: `name="Alice"`, `emp_id="E123"`, `department="HR"`
- Emp B: `name="Bob"`, `emp_id="E456"`, `department="Engineering"`
- Emp C: `name="Charlie"`, `emp_id="ADMIN"`, `department="Finance"`

### Test cases
- `test_search_by_name_still_works`
  - GET `/emp/home/?q=Ali` returns Emp A and excludes others.
- `test_search_by_emp_id`
  - GET `/emp/home/?q=E123` returns Emp A.
- `test_search_by_department`
  - GET `/emp/home/?q=Engin` returns Emp B (partial, case-insensitive).
- `test_empty_q_returns_all`
  - GET `/emp/home/` and GET `/emp/home/?q=` return all created emps.

Assertions:
- Prefer checking `response.context['emps']` (ids or names) vs brittle HTML assertions.

---

## Risks
- Substring ambiguity: queries may match unintended records; acceptable given `icontains` semantics and AC.
- Performance on large datasets: OR `icontains` filters may be slow; out of scope.
- Typos in field names (`emp_id`, `department`) could break filtering; mitigate by tests.

---

## Assumptions
- Home page remains `/emp/home/` and is the only place `q` is interpreted.
- Search is server-side only (no separate API).
- Existing template already submits `q`; no UI change is required to meet AC.

---

## Implementation sequence (dependency-ordered)
1) **Confirm current routing and template wiring**
   - Review `emp/urls.py` and `templates/emp/home.html` to confirm the view endpoint and that `q` is the search parameter.

2) **Update backend search logic**
   - Update `emp/views.py::emp_home`:
     - `from django.db.models import Q`
     - Replace the single-field filter with OR across `name`, `emp_id`, `department`.
     - Keep passing `q` back in context.

3) **Add unit tests**
   - Update `emp/tests.py`:
     - Add fixture data.
     - Add tests for name, emp_id, department search, and empty query.

4) **(Optional) Update README**
   - Add a brief note describing that `q` searches name/employee id/department.

5) **Run tests and smoke check**
   - `python manage.py test`
   - Manual: search by name/id/department from the Home page.

---

## Mapping to Jira Acceptance Criteria
- AC1 (emp_id): backend OR filter + `test_search_by_emp_id`.
- AC2 (department): backend OR filter + `test_search_by_department`.
- AC3 (name regression): `test_search_by_name_still_works`.
- AC4 (keep `q`, no UI change): template untouched; verification step #1.
