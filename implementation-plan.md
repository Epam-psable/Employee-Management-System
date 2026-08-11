# Implementation Plan – EPMCDMETST-59251 – Safe employee deletion (confirmation + POST-only delete)

**Jira Story:** EPMCDMETST-59251 – “Make employee deletion safer: confirmation + POST-only delete with CSRF”  
**Priority:** High

---

## Objective

Make deletion of employee records safer by adding a confirmation step and enforcing that deletion occurs via a **POST** request with **CSRF** protection. After successful deletion, redirect to the employee home page and display a success message.

---

## Scope

- Add a delete confirmation UI flow (confirmation page is acceptable per AC).
- Enforce delete endpoint is **POST-only** and protected by Django CSRF.
- Update the employee list to no longer delete via GET link.
- Show a success message after delete and redirect to `/emp/home/`.
- Add automated tests to cover new behavior.

**Traceability to Acceptance Criteria**
- **AC1**: Delete click prompts confirmation.
- **AC2**: Cancel performs no deletion and returns to list unchanged.
- **AC3**: Confirm delete is **POST** with **CSRF**.
- **AC4**: Redirect to home and show success message after delete.

---

## Out of scope

- Authentication/authorization for delete.
- Soft-delete/audit logging.
- Changes to other CRUD flows or additional search/filter features.
- Any database schema changes.

---

## Existing components (repo analysis)

- **App:** `emp`
  - Routes: `emp/urls.py`
  - Views: `emp/views.py`
  - Templates: `templates/emp/home.html`, `templates/emp/add_emp.html`, `templates/emp/update_emp.html`
- **Current delete implementation**
  - UI: `templates/emp/home.html` uses a GET link: `/emp/delete-emp/{{e.id}}`
  - Route: `path("delete-emp/<int:emp_id>", delete_emp)`
  - View: `delete_emp()` deletes on any method and redirects to `/emp/home/`
- **Messages framework** is enabled in `myapp/settings.py` (middleware and context processor present).

---

## Impacted files

### Backend
- `emp/views.py`
- `emp/urls.py`

### Frontend (templates)
- `templates/emp/home.html`
- `templates/emp/confirm_delete.html` (new)

### Tests
- `emp/tests.py`

---

## Frontend changes

### 1) Employee list (`templates/emp/home.html`)

- Replace current delete anchor:
  - From: `<a href="/emp/delete-emp/{{e.id}}" ...>Delete</a>`
  - To: link to confirmation page, e.g. `/emp/delete-emp/{{e.id}}/confirm/`.

- Add a section to render Django messages (needed for AC4). Example placement: near top of body, under navbar.
  - Render loop over `messages` with Bootstrap alert styles.

### 2) Confirmation page (`templates/emp/confirm_delete.html`) – new

- Show a clear confirmation prompt such as: “Are you sure you want to delete employee X?”
- Provide two actions:
  - **Cancel**: link back to `/emp/home/` (no DB change; meets AC2).
  - **Confirm Delete**: `<form method="post" action="/emp/delete-emp/{{ emp.id }}">` including `{% csrf_token %}` (meets AC3).

---

## Backend changes

### 1) Add confirmation view (GET)

- Add new view function in `emp/views.py`, e.g. `confirm_delete_emp(request, emp_id)`:
  - Accept GET only (or allow GET and reject POST).
  - Fetch employee via `get_object_or_404(Emp, pk=emp_id)`.
  - Render `templates/emp/confirm_delete.html` with context `{ 'emp': emp }`.

### 2) Enforce POST-only delete

- Update existing `delete_emp(request, emp_id)`:
  - Enforce **POST-only** using `@require_POST` (preferred) or method check.
  - Use `get_object_or_404` instead of `Emp.objects.get` to avoid 500.
  - Delete the record.
  - Add success message via `django.contrib.messages`:
    - `messages.success(request, "Employee deleted successfully")`
  - Redirect to `/emp/home/`.

### 3) Routing updates (`emp/urls.py`)

- Add route for confirmation page:
  - `path("delete-emp/<int:emp_id>/confirm/", confirm_delete_emp)`
- Keep existing delete endpoint but it will now accept only POST:
  - `path("delete-emp/<int:emp_id>", delete_emp)`

---

## Database impact

- None. No schema changes or migrations required.
- Do not modify/commit `db.sqlite3`.

---

## Testing strategy

### Automated tests (Django TestCase) – `emp/tests.py`

Add tests to verify acceptance criteria:

1) **Confirmation page renders** (AC1)
- Create an `Emp`.
- GET `/emp/delete-emp/<id>/confirm/` returns 200.

2) **Cancel does not delete** (AC2)
- Since cancel is a GET navigation back to home, validate by:
  - GET confirm page (no deletion).
  - Ensure object still exists.

3) **GET to delete endpoint does not delete** (AC3 enforcement)
- GET `/emp/delete-emp/<id>` should return **405** if `@require_POST` is used.
- Assert employee still exists.

4) **POST delete deletes and sets message** (AC3, AC4)
- POST to `/emp/delete-emp/<id>`.
- Assert redirect to `/emp/home/`.
- Assert employee is deleted.
- Assert a success message exists in the response request using `django.contrib.messages.get_messages`.

### Manual test checklist

- From `/emp/home/`, click Delete → confirm screen appears.
- Click Cancel → return to list, employee still present.
- Click Confirm Delete → employee removed, redirected to home, success message shown.
- Try opening delete URL directly with GET → no deletion (405 or similar behavior).

---

## Risks

- Users accustomed to one-click delete will now need one extra step (expected).
- If messages are not rendered in templates, AC4 will fail (ensure home template renders messages).
- Direct links/bookmarks to old GET delete URL will no longer delete (desired), but may show 405.

---

## Assumptions

- A dedicated confirmation page is acceptable as the “confirmation prompt” (modal not required by AC).
- Django messages framework is acceptable for the success message.
- No authorization is needed for delete (current system has none).

---

## Implementation sequence (dependency-ordered)

1) Update routing (`emp/urls.py`) to add confirm route.
2) Add confirmation view (`confirm_delete_emp`) and template (`templates/emp/confirm_delete.html`).
3) Harden delete view (`delete_emp`) to POST-only + CSRF + message + redirect.
4) Update home list template to use confirmation link instead of delete-by-GET.
5) Add messages rendering block on home page.
6) Add/extend tests in `emp/tests.py`.
7) Run tests and perform manual smoke test.
