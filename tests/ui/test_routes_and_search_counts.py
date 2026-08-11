import re

import pytest
from playwright.sync_api import expect

from .pages import LOC




def _get_card_text(page, label_text: str) -> str:
    # Find the exact <h5> title, then read the number from the next <p>
    title = page.locator(f'h5.card-title:text-is("{label_text}")')
    return title.locator("xpath=following-sibling::p[1]").inner_text()


def test_root_and_index_routes_render_home(ui, page):
    ui.goto("/")
    expect(page.locator(LOC.table)).to_be_visible()

    ui.goto("/index/")
    expect(page.locator(LOC.table)).to_be_visible()


def test_counts_remain_global_when_search_applied(ui, page):
    ui.goto("/emp/home/")

    total_before = _get_card_text(page, "Total Employees")
    active_before = _get_card_text(page, "Active Employees")
    inactive_before = _get_card_text(page, "Inactive Employees")

    page.locator(LOC.search_input).fill("Alice")
    page.locator(LOC.search_button).click()

    expect(page.locator(LOC.table_rows)).to_have_count(1)

    assert _get_card_text(page, "Total Employees") == total_before
    assert _get_card_text(page, "Active Employees") == active_before
    assert _get_card_text(page, "Inactive Employees") == inactive_before


@pytest.mark.xfail(reason="Update department dropdown is not preselected in current template")
def test_update_department_should_be_preselected(ui, page):
    ui.goto("/emp/home/")

    page.locator('table.table tbody tr:has(td:text-is("Marie-Claire")) a:has-text("Update")').click()
    expect(page).to_have_url(re.compile(r"/emp/update-emp/\d+"))

    expect(page.locator(LOC.emp_department)).to_have_value("ME")
