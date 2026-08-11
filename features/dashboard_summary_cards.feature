Feature: Dashboard Summary Cards (EPMCDMETST-56181)
  As a user
  I want to see dashboard summary cards on the Employee Home page
  So that I can quickly understand overall employee status distribution

  Background:
    Given the Employee Management System is running

  Scenario: Dashboard summary cards are displayed on Employee Home page
    When I open the Employee Home page
    Then I should see the "Total Employees" summary card
    And I should see the "Active Employees" summary card
    And I should see the "Inactive Employees" summary card

  Scenario: Dashboard counts are numeric and consistent
    When I open the Employee Home page
    Then the value in "Total Employees" card should be a number
    And the value in "Active Employees" card should be a number
    And the value in "Inactive Employees" card should be a number
    And Total Employees should equal Active Employees plus Inactive Employees

  Scenario: Dashboard counts update after adding an active employee
    Given I note the current values of Total Employees, Active Employees and Inactive Employees
    When I add a new employee with working status set to active
    Then Total Employees should increase by 1
    And Active Employees should increase by 1
    And Inactive Employees should remain unchanged

  Scenario: Dashboard counts update after adding an inactive employee
    Given I note the current values of Total Employees, Active Employees and Inactive Employees
    When I add a new employee with working status set to inactive
    Then Total Employees should increase by 1
    And Inactive Employees should increase by 1
    And Active Employees should remain unchanged

  Scenario: Dashboard counts update after changing an active employee to inactive
    Given an active employee exists
    And I note the current values of Total Employees, Active Employees and Inactive Employees
    When I update the employee and set working status to inactive
    Then Total Employees should remain unchanged
    And Active Employees should decrease by 1
    And Inactive Employees should increase by 1

  Scenario: Dashboard counts update after changing an inactive employee to active
    Given an inactive employee exists
    And I note the current values of Total Employees, Active Employees and Inactive Employees
    When I update the employee and set working status to active
    Then Total Employees should remain unchanged
    And Inactive Employees should decrease by 1
    And Active Employees should increase by 1

  Scenario: Dashboard counts update after deleting an employee
    Given an employee exists
    And I note the current values of Total Employees, Active Employees and Inactive Employees
    When I delete the employee from the employee table
    Then Total Employees should decrease by 1
    And either Active Employees or Inactive Employees should decrease by 1 depending on the deleted employee status

  Scenario: Dashboard counts remain global when a search filter is applied (current behavior)
    Given I note the current values of Total Employees, Active Employees and Inactive Employees
    When I search employees by name with a query that returns a subset of results
    Then the values in Total Employees, Active Employees and Inactive Employees cards should remain unchanged
