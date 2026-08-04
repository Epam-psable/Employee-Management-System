Feature: Employee Search Functionality (EPMCDMETST-56210)
  As a user
  I want to search employees by name
  So that I can quickly find employees in the table

  Background:
    Given the Employee Management System is running
    And I am on the Employee Home page

  Scenario: Search input and Search button are available on Employee Home page
    Then I should see the search input with placeholder "Search by name"
    And I should see the "Search" button

  Scenario: Search by full name returns matching employee rows
    Given employees exist with the following names:
      | name                |
      | Anil Chouhan        |
      | Yuvraj Singh Panwar |
    When I search by name for "Anil Chouhan"
    Then I should see an employee row with name "Anil Chouhan"
    And I should not see an employee row with name "Yuvraj Singh Panwar"

  Scenario: Search by partial name returns all employees whose name contains the query
    Given employees exist with the following names:
      | name           |
      | Aryan Singh    |
      | Yuvraj Singh   |
      | Utkarsh Sharma |
    When I search by name for "Singh"
    Then I should see an employee row with name "Aryan Singh"
    And I should see an employee row with name "Yuvraj Singh"
    And I should not see an employee row with name "Utkarsh Sharma"

  Scenario: Search is case-insensitive
    Given employees exist with the following names:
      | name             |
      | Harshita Agarwal |
    When I search by name for "harshita"
    Then I should see an employee row with name "Harshita Agarwal"

  Scenario: Search trims leading and trailing spaces in the query
    Given employees exist with the following names:
      | name            |
      | Shivangi Tiwari |
    When I search by name for "  Shivangi  "
    Then I should see an employee row with name "Shivangi Tiwari"

  Scenario: Empty search query shows all employees (no filtering)
    Given multiple employees exist
    When I search by name for ""
    Then I should see all employees in the employee table

  Scenario: Whitespace-only search query shows all employees (no filtering)
    Given multiple employees exist
    When I search by name for "   "
    Then I should see all employees in the employee table

  Scenario: No matching results returns an empty employee list without error
    Given multiple employees exist
    When I search by name for "NoSuchEmployeeName_123"
    Then I should see no employee rows in the employee table
    And the page should load successfully

  Scenario: Search query persists in the search input after submitting
    When I search by name for "pooja"
    Then the search input value should be "pooja"

  Scenario: Search works when query is provided directly via URL parameter
    When I open the Employee Home page with search query "pooja" in the URL
    Then I should see employee rows matching the query "pooja"

  Scenario: Dashboard counts remain global when search filter is applied (current behavior)
    Given I note the current values of Total Employees, Active Employees and Inactive Employees
    When I search by name for "pooja"
    Then the values in Total Employees, Active Employees and Inactive Employees cards should remain unchanged
