Feature: Employee CRUD Regression
  As a user
  I want to add, update, and delete employees
  So that I can maintain employee records correctly

  Background:
    Given the Employee Management System is running
    And I am on the Employee Home page

  Scenario: Add an active employee successfully
    When I navigate to the Add Employee page
    And I enter valid employee details with working status set to active
    And I submit the Add Employee form
    Then I should be redirected to the Employee Home page
    And I should see the newly added employee in the Employees Table
    And the employee working status should be "True"

  Scenario: Add an inactive employee successfully
    When I navigate to the Add Employee page
    And I enter valid employee details with working status set to inactive
    And I submit the Add Employee form
    Then I should be redirected to the Employee Home page
    And I should see the newly added employee in the Employees Table
    And the employee working status should be "False"

  Scenario: Update employee details successfully from Employees Table
    Given an employee exists in the Employees Table
    When I click "Update" for that employee
    Then I should see the Update Employee form prefilled with the employee details
    When I update the employee name, phone, and address with valid values
    And I submit the Update Employee form
    Then I should be redirected to the Employee Home page
    And I should see the updated employee details in the Employees Table

  Scenario: Update employee working status successfully
    Given an employee exists in the Employees Table with working status "True"
    When I click "Update" for that employee
    And I set working status to "False"
    And I submit the Update Employee form
    Then I should be redirected to the Employee Home page
    And I should see the employee working status as "False" in the Employees Table

  Scenario: Delete an employee successfully from Employees Table
    Given an employee exists in the Employees Table
    When I click "Delete" for that employee
    Then I should be redirected to the Employee Home page
    And the deleted employee should no longer appear in the Employees Table

  Scenario: Delete an employee from filtered search results
    Given an employee exists with name containing "pooja"
    When I search employees by name for "pooja"
    Then I should see at least one matching employee row in the Employees Table
    When I click "Delete" for a matching employee row
    Then I should be redirected to the Employee Home page
    And the deleted employee should no longer appear in the Employees Table

  Scenario: Navigate using navbar between Home and Add Employee
    When I click "Add Employee" in the navigation bar
    Then I should be on the Add Employee page
    When I click "View Table" in the navigation bar
    Then I should be on the Employee Home page
    And I should see the Employees Table
