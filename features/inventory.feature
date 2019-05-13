Feature: The inventory store service back-end
    As a inventory manager
    I need a RESTful catalog service
    So that I can keep track of all my inventory

Background:
    Given the following inventory
        | id | name       | category      | available | condition | count |
        |  1 | shirt      | clothing      | True      | new       | 1     |
        |  2 | pot        | kitchen       | True      | returned  | 3     |
        |  3 | soap       | bath          | True      | new       | 5	    |

#Issue #78 - DONE BY SAM
Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Inventory Demo REST API Service" in the title
    And I should not see "404 Not Found"

#Issue 77 - DONE BY JEFF
Scenario: Create a Inventory
    When I visit the "Home Page"
    And I set the "Name" to "chair"
    And I set the "Category" to "furniture"
    And I set the "Condition" to "new"
    And I choose "Available" as "True"
    And I set the "Count" to "1"
    And I press the "Create" button
    Then I should see the message "Success"

#Issue 81 - DONE BY JEFF
Scenario: List all Inventory
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "shirt" in the results
    And I should see "pot" in the results
    And I should see "soap" in the results

#Issue 82 - DONE BY SAM
Scenario: List all clothing
    When I visit the "Home Page"
    And I set the "Name" to "shirt"
    And I press the "Search" button
    Then I should see "clothing" in the results
    And I should not see "pot" in the results
    And I should not see "soap" in the results

Scenario: Update a Inventory
  When I visit the "Home Page"
  And I set the "Name" to "shirt"
  And I press the "Search" button
  Then I should see "clothing" in the results
  When I copy the "Id" field
  And I press the "Clear" button
  And I paste the "Id" field
  And I change "Name" to "top"
  And I press the "Update" button
  Then I should see the message "Success"

  #Issue 84 - Action @Nicole

  Scenario: Void an Inventory
    When I visit the "Home Page"
    And I set the "Name" to "shirt"
    And I press the "Search" button
    Then I should see "shirt" in the results
    And I should see "clothing" in the results
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Void" button
    Then I should see the message "Success"


  #Issue 80 - Delete @Nicole
  Scenario: Delete an Inventory
    When I visit the "Home Page"
    And I set the "Name" to "shirt"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "clothing" in the results
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    When I press the "Delete" button
    And I set the "Name" to "shirt"
    And I press the "Search" button
    Then I should not see "shirt" in the "Name" field
    And I should not see "clothing" in the "Category" field
    And the "Id" field should be empty
