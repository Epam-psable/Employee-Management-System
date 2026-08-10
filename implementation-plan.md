# Implementation Plan – EPMCDMETST-59163 (Prevent accidental deletions)

**Jira Story: EPMCDMETST-59163**  
Summary: *Prevent accidental employee deletions by requiring confirmation and POST-only delete*

## Objective
Implement a deletion flow that avoids accidental removal of employee records by:
- requiring user confirmation before deletion, and
- ensuring the delete action is POST-only (GET must not delete data).

This plan must meet the approved acceptance criteria from the Jira story.

## Scope
In scope (must do):
1. Replace the current GET-based delete link with a POST-based delete action.
2. Add a confirmation step before the record is deleted.
3. Ensure key behavior: GET requests to the delete endpoint do not delete anything (405 Method Not Allowed or safe redirect without deleting).
4. Update templates so the user can intentionally confirm deletion.

## Out of scope
- Add/correct model validations for employee create/update
- Add authentication/roles/permissions
- Add undo/soft-delete functionality
- Redesign UI/UX beyond the minimum confirmation requirement
- Any database schema changes (not required)

## Existing components (repo observations)
- Django project: `myapp`, app: `emp`
- UI templates served from `templates/emp/*.html`
- Delete flow today:
  - URL: `path("delete-emp/<int:emp_id>", delete_emp)` (`emp/urls.py`)
  - View: `delete_emp` (`emp/views.py`) accepts GET, fetches Emp by pk, deletes immediately, redirects to `/emp/home/`
  - UI: `templates/emp/home.html` uses an anchor link `<a href="/emp/delete-emp/{{e.id}}">Delete</a>` which triggers a GET deletion.

## Impacted files
### Backend
- `emp/views.py`
- `emp/urls.py`

### Frontend
- `templates/emp/home.html`
- **New** template for confirmation (recommended): `templates/emp/confirm_delete_emp.html` (or under `templates/emp/` naming convention)

### Tests
- `emp/tests.py` (currently minimal; expand with request tests)

## Frontend changes
1. Replace the Delete anchor on the employees table with one of the following patterns:
   - **Option A (recommended, simplest and explicit):** Link to a confirmation page (`GET /emp/delete-emp/<id>/confirm`) that shows details + a POST form to actually delete.
   - **Option B:** Use a Bootstrap modal per row and submit a POST to delete. (More JS/markup; higher risk for this repo.)

2. Confirmation UI requirements (traceable to AC):
   - Clearly display employee identity (name + emp_id) so the user knows what will be deleted.
   - Provide **Confirm** (POST submit) and **Cancel** (back to home) actions.
   - Use `{% csrf_token %}` in the POST form.

3. Home page behavior:
   - Delete action should no longer be a simple GET link that deletes.
   - If using Option A, replace Delete button with `href="{% url 'emp_confirm_delete' e.id %}"` (after URL naming is introduced).

## Backend changes
### URLs (`emp/urls.py`)
Introduce named routes (to avoid hard-coded paths in templates) and split confirmation (GET) from deletion (POST):
- `GET  /emp/delete-emp/<int:emp_id>/` → **confirmation page** (or `/confirm/`)
- `POST /emp/delete-emp/<int:emp_id>/` → **perform deletion** (same path, method-based) OR separate endpoint:
  - `GET  /emp/delete-emp/<int:emp_id>/confirm/` → confirm
  - `POST /emp/delete-emp/<int:emp_id>/delete/` → execute

Recommended for clarity and minimal changes:
- `path("delete-emp/<int:emp_id>/", confirm_delete_emp, name="emp_confirm_delete")`
- `path("delete-emp/<int:emp_id>/do/", do_delete_emp, name="emp_do_delete")`

### Views (`emp/views.py`)
1. Add `confirm_delete_emp(request, emp_id)`:
   - `GET` only: fetch employee by pk (use `get_object_or_404`)
   - render confirmation template with employee context

2. Add/modify `do_delete_emp(request, emp_id)`:
   - enforce POST-only using one of:
     - `@require_POST` decorator (recommended)
     - manual check: `if request.method != "POST": return HttpResponseNotAllowed([...])`
   - fetch employee by pk and delete
   - redirect to `/emp/home/`

3. Ensure “GET must not delete” acceptance criterion:
   - `do_delete_emp` must reject GET (405 or safe redirect without deleting)

4. Error handling:
   - If employee does not exist, return 404 (via `get_object_or_404`).

## Database impact
None expected.
- No model/schema changes.
- No migrations required.

## Testing strategy
Add Django tests using `django.test.TestCase` + `Client`.

### Unit/Request tests (minimum)
1. **GET confirm page**
   - Create an `Emp` instance
   - `GET /emp/delete-emp/<id>/` returns 200
   - Response contains employee name/identifier

2. **POST delete executes**
   - Create an `Emp`
   - `POST /emp/delete-emp/<id>/do/` deletes record
   - Verify redirect to `/emp/home/`
   - Verify object no longer exists

3. **GET on do_delete endpoint does not delete** (AC2)
   - Create an `Emp`
   - `GET /emp/delete-emp/<id>/do/` returns 405 (or 302 redirect) but **record remains**

4. **CSRF**
   - Template includes `{% csrf_token %}` (can be validated by checking rendered HTML contains `csrfmiddlewaretoken`)

### Manual verification checklist
- On Home, clicking Delete shows confirmation step.
- Cancel returns to Home without changes.
- Confirm removes employee and returns to Home without the deleted employee.
- Directly opening delete execution URL via browser GET does not delete.

## Risks
- Existing UI uses hard-coded URLs; introducing named URLs requires updating templates consistently.
- If deletion is currently triggered via GET in multiple templates, missing one could leave a dangerous path.
- Adding a modal-based confirmation (if chosen) can be error-prone in a template-only app without JS structure.

## Assumptions
- No authentication is required for delete in this story.
- Using server-rendered templates is acceptable for the confirmation step.
- Returning HTTP 405 for GET on the POST-only endpoint satisfies the “method not allowed or redirected safely” requirement.

## Implementation sequence (dependency-ordered)
1. **Repository analysis and baseline**
   - Locate current delete link usage (at least `templates/emp/home.html`).
   - Locate current delete route and view (`emp/urls.py`, `emp/views.py`).

2. **Backend: Add new views**
   - Implement `confirm_delete_emp` (GET-only) using `get_object_or_404`.
   - Implement `do_delete_emp` with `@require_POST` (or 405) and deletion logic.

3. **Backend: Update URL configuration**
   - Add/replace URL patterns to route to confirm + do-delete.
   - Add `name=` for URLs and use them in templates.

4. **Frontend: Add confirmation template**
   - Create `templates/emp/confirm_delete_emp.html`.
   - Include a POST form to `emp_do_delete` with CSRF token.
   - Provide cancel navigation.

5. **Frontend: Update Home delete action**
   - Replace delete anchor that performs deletion with link to confirmation page.
   - Prefer `{% url %}` tags over hard-coded paths.

6. **Tests**
   - Add/expand tests in `emp/tests.py` for confirm page, post deletion, GET-blocking.

7. **Final verification**
   - Run test suite.
   - Manually confirm acceptance criteria behavior in browser.
