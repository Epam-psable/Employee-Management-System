import re

import pytest
from playwright.sync_api import expect

from .pages import LOC, action_link_in_row, row_by_employee_id, row_by_employee_name


def _extract_first_int(text: str) -> int:
    m = re.search(r"(\d+)", text)
    assert m, f"No integer found in: {text!r}"
    return int(m.group(1))


def _get_counts(page):
    # In template: <div class="card-body"><h5 ...>Label</h5><p ...>NUMBER</p></div>
    total = _extract_first_int(
        page.locator(LOC.total_card).locator("xpath=following-sibling::p[1]").inner_text()
    )
    active = _extract_first_int(
        page.locator(LOC.active_card).locator("xpath=following-sibling::p[1]").inner_text()
    )
    inactive = _extract_first_int(
        page.locator(LOC.inactive_card).locator("xpath=following-sibling::p[1]").inner_text()
    )
    return total, active, inactive


def test_home_loads_and_dashboard_visible(ui, page):
    ui.goto("/emp/home/")

    expect(page.locator(LOC.total_card)).to_be_visible()
    expect(page.locator(LOC.active_card)).to_be_visible()
    expect(page.locator(LOC.inactive_card)).to_be_visible()

    expect(page.locator(LOC.table)).to_be_visible()
    expect(page.locator(LOC.table_rows)).to_have_count(6)


def test_search_filters_by_name_and_persists_query(ui, page):
    ui.goto("/emp/home/")

    page.locator(LOC.search_input).fill("John")
    page.locator(LOC.search_button).click()

    # Matches: John Doe, johnson smith, Alice Johnson
    expect(page.locator(LOC.table_rows)).to_have_count(3)
    expect(page.locator(LOC.search_input)).to_have_value("John")

    # Case-insensitive
    page.locator(LOC.search_input).fill("joHN")
    page.locator(LOC.search_button).click()
    expect(page.locator(LOC.table_rows)).to_have_count(3)

    # Trim
    page.locator(LOC.search_input).fill("  Alice  ")
    page.locator(LOC.search_button).click()
    expect(page.locator(LOC.table_rows)).to_have_count(1)
    expect(page.locator(row_by_employee_name("Alice Johnson"))).to_be_visible()

    # No match
    page.locator(LOC.search_input).fill("zzzz_no_match_zzzz")
    page.locator(LOC.search_button).click()
    expect(page.locator(LOC.table_rows)).to_have_count(0)


def test_add_employee_updates_table_and_counts(ui, page):
    ui.goto("/emp/home/")
    total0, active0, inactive0 = _get_counts(page)

    page.locator(LOC.add_emp_link).click()
    expect(page).to_have_url(re.compile(r"/emp/add-emp/"))

    # Use unique values to avoid collisions across reruns or parallel execution
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
    expect(page.locator(row_by_employee_id(unique_id))).to_be_visible()

    total1, active1, inactive1 = _get_counts(page)
    assert total1 == total0 + 1
    assert active1 == active0 + 1
    assert inactive1 == inactive0


def test_update_employee_name_and_toggle_working_affects_counts(ui, page):
    ui.goto("/emp/home/")
    total0, active0, inactive0 = _get_counts(page)

    row = row_by_employee_name("John Doe")
    page.locator(action_link_in_row(row, "Update")).click()
    expect(page).to_have_url(re.compile(r"/emp/update-emp/\d+"))

    expect(page.locator(LOC.emp_name)).to_have_value("John Doe")
    expect(page.locator(LOC.emp_working)).to_be_checked()

    page.locator(LOC.emp_name).fill("John Doe Updated")
    page.locator(LOC.emp_working).uncheck()
    page.locator(LOC.submit_update_employee).click()

    expect(page).to_have_url(re.compile(r"/emp/home/"))
    expect(page.locator(row_by_employee_name("John Doe Updated"))).to_be_visible()

    total1, active1, inactive1 = _get_counts(page)
    assert total1 == total0
    assert active1 == active0 - 1
    assert inactive1 == inactive0 + 1


def test_delete_employee_removes_row_and_updates_counts(ui, page):
    ui.goto("/emp/home/")
    total0, active0, inactive0 = _get_counts(page)

    row = row_by_employee_name("johnson smith")

    # Make navigation deterministic
    with page.expect_navigation(url=re.compile(r".*/emp/home/")):
        page.locator(action_link_in_row(row, "Delete")).click()

    expect(page.locator(row_by_employee_name("johnson smith"))).to_have_count(0)

    total1, active1, inactive1 = _get_counts(page)
    assert total1 == total0 - 1
    assert active1 == active0
    assert inactive1 == inactive0 - 1


@pytest.mark.xfail(reason="Current implementation raises DoesNotExist -> 500 for invalid delete id")
def test_delete_invalid_id_should_be_handled_gracefully(ui, page):
    ui.goto("/emp/delete-emp/999999")
    expect(page.locator("text=Server Error")).to_have_count(0)
