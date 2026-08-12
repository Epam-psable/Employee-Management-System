# Implementation Plan - EPMCDMETST-59460

## Jira User Story (reference)
- **Key**: EPMCDMETST-59460
- **Summary**: Make employee deletion safer with confirmation and POST-only delete
- **Priority**: Medium
- **Acceptance Criteria**:
  1. Clicking “Delete” prompts the user to confirm deletion.
  2. Employee is deleted only after confirmation and via a POST request.
  3. After successful deletion, the user is redirected to the home page and the employee no longer appears in the list.
  4. If deletion is cancelled, no data changes occur.

## Objective
Make employee deletion more intentional, safe, and standards-compliant by:
- Removing delete actions from GET links (avoid accidental/unintended deletes).
- Requiring explicit user confirmation before deleting an employee.
- Ensuring delete is performed via POST-only with CSRF protection.

---

## Scope
In scope:
1. UI change on the employee list (home page) to present a confirmation step prior to delete.
2. Change delete flow to submit a POST request (not GET).
3. Backend hardening: only perform delete on POST; otherwise reject/redirect without deleting.
4. Add tests for POST-only behavior and successful deletion.

## Out of scope
- Soft delete / archiving.
- Authentication/authorization changes.
- Bulk delete.
- Changes to add/update employee flows.

---

## Existing components (repo observations)
- **Django app**: `emp`
- **URL route**: `emp/urls.py` currently maps `path("delete-emp/<int:emp_id>", delete_emp)`.
- **View**: `emp/views.py::delete_emp` currently deletes immediately regardless of method:
  - `emp=Emp.objects.get(pk=emp_id)` then `emp.delete()` then redirect.
- **Template**: `templates/emp/home.html` renders delete as a GET link:
  - `<a href="/emp/delete-emp/{{e.id}}" class="btn btn-danger btn-sm">Delete</a>`

---

## Impacted files
Expected direct changes:
- `emp/views.py` — enforce POST-only delete, handle non-POST safely.
- `templates/emp/home.html` — replace GET delete link with POST form + confirmation.
- `emp/tests.py` — add tests covering POST-only and successful POST delete.

Optional / confirm during implementation:
- `emp/urls.py` — may remain unchanged (same URL, different HTTP method handling). Optionally add a dedicated confirm route/template if required.

---

## Frontend changes
**Goal:** ensure users confirm deletion, and that the delete action sends a POST request with CSRF token.

### Preferred approach (minimal): POST form + native confirm()
In `templates/emp/home.html`:
- Replace the delete `<a>` with a small inline `<form method="POST" action="/emp/delete-emp/{{ e.id }}">`.
- Add `{% csrf_token %}`.
- Add confirmation via `onsubmit="return confirm('Are you sure you want to delete this employee?');"`.
- Keep styling consistent (Bootstrap). For example:
  - Use `style="display:inline;"` on the form so it stays in the table action column.

**Acceptance criteria mapping:**
- AC1: Browser confirm dialog prompts user.
- AC4: If user cancels, form submission is aborted and no backend call is made.

### Alternate approach (if required): Bootstrap modal
If the product requires a styled modal instead of browser confirm:
- Add a single Bootstrap modal component to the page.
- Each Delete button sets the target employee id (via data attributes) and updates the modal form action.
- Confirm button submits the POST form.

(Plan assumes the minimal confirm() approach unless UX requirements specify otherwise.)

---

## Backend changes
### 1) Enforce POST-only delete
In `emp/views.py::delete_emp(request, emp_id)`:
- Only delete when `request.method == "POST"`.
- For GET/other methods:
  - Option A (strict): return `HttpResponseNotAllowed(["POST"])`.
  - Option B (tolerant): redirect to `/emp/home/` without deleting.

**Recommendation:** Option A is more correct; Option B is friendlier. Choose one and align tests accordingly.

### 2) Handle missing records gracefully
Currently `Emp.objects.get(pk=emp_id)` will raise `Emp.DoesNotExist` and 500.
- Use `get_object_or_404(Emp, pk=emp_id)` OR handle `DoesNotExist` and redirect.

### 3) Redirect after successful delete
After deleting, redirect to `/emp/home/` (matches current behavior and AC3).

---

## Database impact
None.

---

## Testing strategy
Add Django tests in `emp/tests.py` using `django.test.TestCase` and the test client.

### Test cases
1) **GET does not delete (POST-only enforced)**
- Create an `Emp` record.
- Issue GET to `/emp/delete-emp/<id>`.
- Assert record still exists.
- Assert response is either:
  - 405 (if using HttpResponseNotAllowed), OR
  - 302 redirect to `/emp/home/` (if using tolerant redirect).

2) **POST deletes and redirects**
- Create an `Emp` record.
- Issue POST to `/emp/delete-emp/<id>`.
- Assert response is redirect to `/emp/home/`.
- Assert record no longer exists.

3) **Cancel behavior**
This is primarily client-side. We validate it indirectly by ensuring GET cannot delete (AC4 server-side safety) and via manual verification.

---

## Security considerations
- Deleting via POST reduces CSRF risk compared to GET.
- Ensure `{% csrf_token %}` is included in the delete form.
- Ensure the backend rejects non-POST methods.

---

## Risks
- Other pages/templates might still use the old GET delete link.
  - Mitigation: repo-wide search for `/emp/delete-emp/` and update all occurrences.
- If CSRF token is omitted, POST delete will fail with 403.
  - Mitigation: add token and test the flow.
- Behavior change for users who bookmarked the delete URL.
  - Mitigation: GET should not delete; optionally redirect them safely.

---

## Assumptions
- No authentication/permissions currently in scope.
- Confirmation can be implemented as a browser confirm() dialog.
- The delete endpoint URL stays the same; only HTTP method changes.

---

## Implementation sequence (dependency-ordered)
1. **Repository scan**
   - Locate all delete links/actions (search for `delete-emp` across templates).
2. **Backend: harden delete endpoint**
   - Update `emp/views.py::delete_emp` to enforce POST-only and handle missing employee id safely.
3. **Frontend: update home page delete control**
   - Modify `templates/emp/home.html` to use a POST form + CSRF + confirmation.
4. **Tests**
   - Update `emp/tests.py` with GET-not-delete and POST-delete tests.
5. **Manual verification**
   - Navigate to `/emp/home/`.
   - Click Delete → confirm prompt appears.
   - Cancel → employee remains.
   - Confirm → employee removed and redirected.
   - Try visiting delete URL directly (GET) → should not delete.

---

## Verification steps (post-implementation)
- **AC1:** Clicking Delete prompts confirmation.
- **AC2:** Network/devtools shows POST request with CSRF token and no delete on GET.
- **AC3:** After confirm, redirect to home and employee removed from list.
- **AC4:** Cancel results in no deletion; GET requests also do not delete.
