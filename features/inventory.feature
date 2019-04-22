Feature: The inventory store service back-end
    As a inventory manager
    I need a RESTful catalog service
    So that I can keep track of all my inventory

Background:
    Given the following inventory
        | id | name       | category      | available |
        |  1 | shirt      | clothing      | True      |
        |  2 | pot        | kitchen       | True      |
        |  3 | soap       | bath          | True      |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Inventory Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Inventory
    When I visit the "Home Page"
    And I set the "Name" to "Happy"
    And I set the "Category" to "Hippo"
    And I press the "Create" button
    Then I should see the message "Success"

Scenario: List all Inventory
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "shirt" in the results
    And I should see "pot" in the results
    And I should see "soap" in the results

Scenario: List all clothing
    When I visit the "Home Page"
    And I set the "Category" to "clothing"
    And I press the "Search" button
    Then I should see "shirt" in the results
    And I should not see "pot" in the results
    And I should not see "soap" in the results

Scenario: Update a Pet
    When I visit the "Home Page"
    And I set the "Id" to "1"
    And I press the "Retrieve" button
    Then I should see "shirt" in the "Name" field
    When I change "Name" to "sweatshirt"
    And I press the "Update" button
    Then I should see the message "Success"
    When I set the "Id" to "1"
    And I press the "Retrieve" button
    Then I should see "sweatshirt" in the "Name" field
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see "sweatshirt" in the results
    Then I should not see "shirt" in the results
