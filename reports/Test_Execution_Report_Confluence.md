h1. Test Execution Report — Employee Management System

h2. Project Summary
This report covers the latest automated UI test execution for the *Employee Management System* focusing on:
* Dashboard workforce summary cards (Total/Active/Inactive employees)
* Employee name search on the Employee Home page
* Regression coverage for core CRUD paths to ensure no unintended impact

*Automation Stack:* Pytest + Playwright (Chromium) with Allure result artifacts.

h2. Stories Covered
|| Jira Story || Title || Status ||
| EPMCDMETST-56181 | View Employee Summary Cards on Dashboard | Resolved |
| EPMCDMETST-56210 | Employee Search Functionality | Closed |

h2. Test Environment
|| Item || Details ||
| OS | Windows (win32) |
| Application | Employee Management System (Django) |
| Database | SQLite |
| Test DB Strategy | Isolated SQLite DB per run via `EMS_UI_TEST_DB` (per `tests/README_UI_TESTS.md`) |
| Server | Django `runserver` started by tests on `http://127.0.0.1:8001` (per test doc) |
| Browser | Playwright *Chromium* |
| Framework | Pytest + Playwright |
| Reporting Artifacts | Allure raw results in `reports/allure-results/` |

h2. Test Suite Executed
|| Suite/Area || Location || Notes ||
| UI E2E Core | `tests/ui/test_e2e_core.py` | Core smoke/regression coverage (home, search, add, delete; update marked xfail) |
| CRUD + Search + Dashboard (extended) | `tests/ui/test_smoke_crud_search_dashboard.py` | Broader validations incl. count updates and search behaviors; includes xfail scenario for invalid delete id |
| Routes + Search/Counts | `tests/ui/test_routes_and_search_counts.py` | Validates counts remain global when search is applied; includes xfail for department preselect |

*Note:* Latest Allure run artifacts indicate *5 executed tests* (see Results Summary below). The repository also contains additional test modules and feature files that may not have been part of this specific execution.

h2. Test Results Summary
*Evidence source:* latest Allure result files under `reports/allure-results/*-result.json`.

*Execution outcome (from latest Allure artifacts):*
* Total tests executed: *5*
* Passed: *5*
* Failed: *0*
* Broken: *0*
* Skipped: *0*
* Execution duration (min→max across tests): *~16.014 seconds*
* Overall outcome: *PASS*

h2. Pass/Fail Statistics
|| Metric || Count || Percentage ||
| Total | 5 | 100% |
| Passed | 5 | 100% |
| Failed | 0 | 0% |
| Broken | 0 | 0% |
| Skipped | 0 | 0% |

h2. Acceptance Criteria Coverage

h3. EPMCDMETST-56181 — View Employee Summary Cards on Dashboard
|| Acceptance Criteria || Coverage (Automated Tests) || Result ||
| Dashboard displays exactly three Bootstrap cards (Total/Active/Inactive) | `test_home_dashboard_and_table_render` (tests.ui.test_e2e_core) | PASS *(latest run)* |
| Total Employees = count of all Employee records | `test_add_employee_increases_total_at_least_by_one` (tests.ui.test_e2e_core) | PASS *(latest run)* |
| Active Employees = count where working=True | *Not explicitly proven by latest 5-test run artifacts* | Not Confirmed |
| Inactive Employees = count where working=False | *Not explicitly proven by latest 5-test run artifacts* | Not Confirmed |
| Counts update after Add, Update, Delete operations | Add: `test_add_employee_increases_total_at_least_by_one`; Delete: `test_delete_employee_redirects_and_removes_row` | PASS *(Add/Delete in latest run)*; Update *Not executed/validated in latest run* |
| If no employees exist, all cards display 0 | *Not covered in current suite/run* | Not Covered |

h3. EPMCDMETST-56210 — Employee Search Functionality
|| Acceptance Criteria || Coverage (Automated Tests) || Result ||
| Search box displayed above the employee table | Indirectly verified via successful interaction in `test_search_by_name_filters_results` | PASS *(latest run)* |
| Users can search employees by name | `test_search_by_name_filters_results` (tests.ui.test_e2e_core) | PASS *(latest run)* |
| Search is case insensitive | *Not validated in latest 5-test run artifacts* (present in `test_search_filters_by_name_and_persists_query` in another module) | Not Confirmed |
| Partial matches supported | *Not validated in latest 5-test run artifacts* (present in extended smoke module) | Not Confirmed |
| Empty search returns all employees | *Not validated in latest 5-test run artifacts* | Not Confirmed |
| Existing CRUD functionality remains unchanged | Add/Delete validated in latest run; Update not validated | Partial |
| Results displayed on existing Employee Home page | `test_search_by_name_filters_results` asserts filtering and input persistence on same page | PASS *(latest run)* |

h2. Overall Test Status
*Overall Status:* *PASS* (based on latest Allure execution artifacts: 5/5 passed)

*Quality note:* While the latest executed set is fully passing, not all acceptance criteria are conclusively covered by the latest run’s executed tests (see “Not Confirmed/Not Covered” items above). Additional tests exist in the repo that appear to cover case-insensitivity/partial matches/count updates more thoroughly, but they were not part of the latest Allure execution set captured.

h2. Recommendations
1. *Increase AC-level coverage for this release scope* by executing the broader UI suites (e.g., `tests/ui/test_smoke_crud_search_dashboard.py`) and publishing the resulting Allure report so that:
   * Case-insensitive search
   * Partial match search
   * Empty search returns all
   * Active/Inactive count correctness
   * Add/Update/Delete count updates
   are evidenced in the same execution.
2. *Add a dedicated “no employees” scenario* to validate dashboard cards display 0 when dataset is empty.
3. *Improve traceability:* tag tests with Jira IDs (e.g., Allure labels) so coverage mapping is automatic and audit-ready.
4. *Publish a full Allure HTML report (`allure-report/`)* in CI for easy review, not only raw `allure-results`.
