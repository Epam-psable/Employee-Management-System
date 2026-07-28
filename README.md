# Employee Management System

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![Bootstrap](https://img.shields.io/badge/bootstrap-%23563D7C.svg?style=for-the-badge&logo=bootstrap&logoColor=white)
![VS Code Insiders](https://img.shields.io/badge/VS%20Code%20Insiders-35b393.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white)

A Django-based Employee Management System supporting core employee CRUD operations, enhanced with a dashboard summary and employee search. The project was extended as part of an **AI-assisted SDLC capstone**, including automated UI testing (Playwright + Pytest) and Allure reporting, with traceability via Jira and Confluence documentation.

---

## 1. Project Overview

The Employee Management System (EMS) is a lightweight web application used to manage employee records. It provides a simple UI for creating, viewing, updating, and deleting employees, and includes usability enhancements like a dashboard summary and name-based search.

> This application was created using Python, Django, HTML/CSS, and Bootstrap.

---

## 2. Existing Features

- Add employee details (Name, ID, Phone, Address, Working Status, Department)
- Single form workflow for data entry
- Department selection via dropdown; working status via checkbox
- Employee list/table on the Home page
- Update existing employee details (prefilled form)
- Delete employee records with a single click

---

## 3. New Features Implemented

### Dashboard Summary

The Home page includes summary cards displaying:

- Total Employees
- Active Employees
- Inactive Employees

### Employee Search Functionality

- Search employees by name directly on the Home page
- Search results displayed within the existing employee table view

---

## 4. AI-Assisted SDLC Overview

This capstone used an AI-assisted SDLC workflow to plan, implement, validate, and document enhancements.

### Business Analyst Assistant

- Helped translate enhancement requests into structured requirements and acceptance criteria
- Ensured scope remained limited to implemented features

### Design Assistant

- Supported UX-level design decisions (dashboard layout, search placement) aligned with the existing UI

### Development Assistant

- Assisted with implementation guidance and code-level suggestions for Django views/templates and test scaffolding

### DevOps Assistant

- Provided support for repeatable local execution patterns and test/report automation workflows

### QA Assistant

- Helped design automated UI test coverage using Playwright + Pytest
- Supported creation and interpretation of Allure results

### Human-in-the-Loop approval process

- All key deliverables (requirements, test report, documentation outputs) were reviewed and approved before publishing (e.g., Confluence publishing approval)

---

## 5. Technology Stack

- **Backend:** Python, Django
- **Frontend:** HTML/CSS, Bootstrap
- **Database:** SQLite
- **Automated Testing:** Pytest, Playwright (Chromium)
- **Reporting:** Allure (raw results + report generation)
- **Process & Documentation:** Jira stories + Confluence pages

---

## 6. Installation

### Prerequisites

- **Python** 3.8+
- **Django** 4.x recommended
- (For UI tests) Playwright supported environment

### Setup

```bash
# (Optional but recommended) create & activate a virtual environment
python -m venv .venv
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Install dependencies (if requirements file is available in your setup)
# pip install -r requirements.txt

# Apply migrations
python manage.py migrate
```

---

## 7. Running the Application

```bash
python manage.py runserver
```

Then open:

- http://127.0.0.1:8000/

---

## 8. Automated Testing

Automated UI tests are implemented using **Pytest + Playwright** with **Allure** result artifacts.

### Playwright

Playwright runs browser-based UI tests using **Chromium**.

### Pytest

Pytest is used as the test runner and for fixtures.

### Allure Report generation

Run UI tests (example):

```bash
pytest
```

If you are generating Allure results, ensure tests are run with Allure enabled and results are written to:

- `reports/allure-results/`

Generate an Allure HTML report (if Allure CLI is installed):

```bash
allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report
```

> Notes:
>
> - The repository includes helper tooling/scripts under `reports/` for working with Allure raw results.
> - See `tests/README_UI_TESTS.md` for the project-specific UI test run approach.

---

## 9. Project Structure (brief overview)

- `emp/` — Core Django app (models, views, urls, migrations)
- `myapp/` — Django project configuration (settings, urls, wsgi/asgi)
- `templates/` / UI files — HTML templates (if present in your environment)
- `tests/` — Automated tests (UI tests using Playwright + Pytest)
- `reports/` — Test artifacts and Allure result utilities
- `features/` — Feature specifications used for coverage/reference

---

## 10. Enhancements Delivered

Completed and reflected in this repository:

- CRUD Operations (existing capability)
- Dashboard Summary (Total/Active/Inactive)
- Employee Search by name
- Playwright automated UI tests (Pytest runner)
- Allure results generation and reporting workflow
- Jira and Confluence documentation produced as part of the capstone
- AI-assisted SDLC workflow with human approvals

---

## 11. Future Improvements (optional)

- Expand automated coverage for edge cases (e.g., empty dataset dashboard = 0 counts)
- Add CI pipeline to publish Allure HTML reports automatically
- Improve search capabilities (e.g., search by department, phone, ID) if required by future scope
- Add role-based access/authentication for admin vs. viewer roles

---

## 12. License

MIT

**Free Software, Hell Yeah!**
