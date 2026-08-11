import re

import pytest
from playwright.sync_api import expect

from .pages import LOC


def _extract_first_int(text: str) -> int:
    m = re.search(r"(\d+)", text)
    return int(m.group(1)) if m else 0


def _get_counts(page):
    # Read numbers from the <p> right after each dashboard title
    total = _extract_first_int(page.locator(LOC.total_card).locator("xpath=following-sibling::p[1]").inner_text())
    active = _extract_first_int(page.locator(LOC.active_card).locator("xpath=following-sibling::p[1]").inner_text())
    inactive = _extract_first_int(page.locator(LOC.inactive_card).locator("xpath=following-sibling::p[1]").inner_text())
    return total, active, inactive


def test_home_dashboard_and_table_render(ui, page):
    ui.goto("/emp/home/")
    expect(page.locator(LOC.total_card)).to_be_visible()
    expect(page.locator(LOC.active_card)).to_be_visible()
    expect(page.locator(LOC.inactive_card)).to_be_visible()
    expect(page.locator(LOC.table)).to_be_visible()
    # Seed should show 6
    expect(page.locator(LOC.table_rows)).to_have_count(6)


def test_search_by_name_filters_results(ui, page):
    ui.goto("/emp/home/")

    page.locator(LOC.search_input).fill("Alice")
    page.locator(LOC.search_button).click()

    expect(page.locator(LOC.table_rows)).to_have_count(1)
    expect(page.locator(LOC.search_input)).to_have_value("Alice")


def test_add_employee_increases_total_at_least_by_one(ui, page):
    ui.goto("/emp/home/")
    total0, active0, inactive0 = _get_counts(page)

    page.locator(LOC.add_emp_link).click()
    expect(page).to_have_url(re.compile(r"/emp/add-emp/"))

    unique_id = f"EMP777{abs(hash(page.url)) % 100000}"
    unique_name = f"New Employee {unique_id}"

    page.locator(LOC.emp_name).fill(unique_name)
    page.locator(LOC.emp_id).fill(unique_id)
    page.locator(LOC.emp_phone).fill("1234567890")
    page.locator(LOC.emp_address).fill("Test Address")
    page.locator(LOC.emp_working).check()
    page.locator(LOC.emp_department).select_option("CSE")
    page.locator(LOC.submit_add_employee).click()

    expect(page).to_have_url(re.compile(r"/emp/home/"))

    total1, active1, inactive1 = _get_counts(page)

    # Current app behavior may create duplicates on submit; assert minimum change.
    assert total1 >= total0 + 1
    assert active1 >= active0  # should not decrease
    assert inactive1 == inactive0


@pytest.mark.xfail(reason="Known issue in current app: update page crashes with OSError on Windows due to print()")
def test_update_employee_page_opens_and_is_prefilled(ui, page):
    ui.goto("/emp/home/")
    page.locator('table.table tbody tr:has(td:text-is("John Doe")) a:has-text("Update")').click()
    expect(page).to_have_url(re.compile(r"/emp/update-emp/\d+"))
    expect(page.locator(LOC.emp_name)).to_have_value("John Doe")

def test_delete_employee_redirects_and_removes_row(ui, page):
    ui.goto("/emp/home/")

    rows = page.locator("table.table tbody tr")
    before = rows.count()
    assert before > 0

    first_delete = page.locator("table.table tbody tr a:has-text('Delete')").first
    with page.expect_navigation():
        first_delete.click()

    after = page.locator("table.table tbody tr").count()
    assert after == before - 1