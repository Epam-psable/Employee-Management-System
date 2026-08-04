from dataclasses import dataclass


@dataclass(frozen=True)
class Locators:
    # Home/Search
    search_input: str = 'input[name="q"]'
    search_button: str = 'button:has-text("Search")'

    # Dashboard cards (labels)
    # Use exact match to avoid strict-mode collisions (e.g., "Active" inside "Inactive").
    total_card: str = 'h5.card-title:text-is("Total Employees")'
    active_card: str = 'h5.card-title:text-is("Active Employees")'
    inactive_card: str = 'h5.card-title:text-is("Inactive Employees")'

    # Table
    table: str = 'table.table'
    table_rows: str = 'table.table tbody tr'

    # Navbar links
    add_emp_link: str = 'a:has-text("Add Employee")'
    view_table_link: str = 'a:has-text("View Table")'

    # Add/Update form fields
    emp_name: str = 'input[name="emp_name"]'
    emp_id: str = 'input[name="emp_id"]'
    emp_phone: str = 'input[name="emp_phone"]'
    # In templates, address is a <textarea>
    emp_address: str = 'textarea[name="emp_address"]'
    emp_working: str = 'input[name="emp_working"]'
    emp_department: str = 'select[name="emp_department"]'
    # Buttons in templates often lack type="submit"; select by visible text.
    submit_add_employee: str = 'button:has-text("Add Employee")'
    submit_update_employee: str = 'button:has-text("Update Employee")'


LOC = Locators()


def row_by_employee_name(name: str) -> str:
    return f'table.table tbody tr:has(td:text-is("{name}"))'


def row_by_employee_id(emp_id: str) -> str:
    # ID is displayed in a dedicated column, so use exact cell match.
    return f'table.table tbody tr:has(td:text-is("{emp_id}"))'


def row_by_employee_id(emp_id: str) -> str:
    # ID is displayed in a dedicated column, so use exact cell match.
    return f'table.table tbody tr:has(td:text-is("{emp_id}"))'


def row_by_employee_id(emp_id: str) -> str:
    # ID is displayed in a dedicated column, so use exact cell match.
    return f'table.table tbody tr:has(td:text-is("{emp_id}"))'


def action_link_in_row(row_selector: str, action_text: str) -> str:
    return f'{row_selector} a:has-text("{action_text}")'
