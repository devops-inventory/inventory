# Copyright 2016, 2017 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Inventory Model

Test cases can be run with:
  nosetests
  coverage report -m
"""

import unittest
import os
from app.models import Inventory, DataValidationError, db
from app import app

DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')

######################################################################
#  T E S T   C A S E S
######################################################################
class TestInventory(unittest.TestCase):
    """ Test Cases for Inventory """

    @classmethod
    def setUpClass(cls):
        """ These run once per Test suite """
        app.debug = False
        # Set up the test database
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        Inventory.init_db(app)
        db.drop_all()    # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_a_inventory(self):
        testcases_new_attributes
        """ Create inventory and assert that it exists """
        inventory = Inventory(name="tools", category="widget1", available=True)
        master
        self.assertTrue(inventory != None)
        self.assertEqual(inventory.id, None)
        self.assertEqual(inventory.name, "tools")
        self.assertEqual(inventory.category, "widget1")
        self.assertEqual(inventory.available, True)

    def test_add_a_inventory(self):
        """ Create an inventory and add it to the database """
        inventorys = Inventory.all()
        self.assertEqual(inventorys, [])
        inventory = Inventory(name="tools", category="widget1", available=True)
        self.assertTrue(inventory != None)
        self.assertEqual(inventory.id, None)
        inventory.save()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(inventory.id, 1)
        inventorys = Inventory.all()
        self.assertEqual(len(inventorys), 1)

    def test_update_a_inventory(self):
        """ Update an Inventory """
        inventory = Inventory(name="tool", category="widget1", available=True)
        inventory.save()
        self.assertEqual(inventory.id, 1)
        # Change it an save it
        inventory.category = "jkwidget2"
        inventory.save()
        self.assertEqual(inventory.id, 1)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        inventorys = Inventory.all()
        self.assertEqual(len(inventorys), 1)
        self.assertEqual(inventorys[0].category, "jkwidget2")

    def test_delete_a_inventory(self):
        """ Delete an inventory """
        inventory = Inventory(name="tools", category="widget1", available=True)
        inventory.save()
        self.assertEqual(len(Inventory.all()), 1)
        # delete the inventory and make sure it isn't in the database
        inventory.delete()
        self.assertEqual(len(Inventory.all()), 0)

    def test_serialize_a_inventory(self):
        """ Test serialization of a Inventory """
        inventory = Inventory(name="tools", category="widget1", available=False)
        data = inventory.serialize()
        self.assertNotEqual(data, None)
        self.assertIn('id', data)
        self.assertEqual(data['id'], None)
        self.assertIn('name', data)
        self.assertEqual(data['name'], "tools")
        self.assertIn('category', data)
        self.assertEqual(data['category'], "widget1")
        self.assertIn('available', data)
        self.assertEqual(data['available'], False)

    def test_deserialize_a_inventory(self):
        """ Test deserialization of a Inventory """
        data = {"id": 1, "name": "materials", "category": "widget2", "available": True, "count":1,"condition":"new"}
        inventory = Inventory()
        inventory.deserialize(data)
        self.assertNotEqual(inventory, None)
        self.assertEqual(inventory.id, None)
        self.assertEqual(inventory.name, "materials")
        self.assertEqual(inventory.category, "widget2")
        self.assertEqual(inventory.available, True)

    def test_deserialize_bad_data(self):
        """ Test deserialization of bad data """
        data = "this is not a dictionary"
        inventory = Inventory()
        self.assertRaises(DataValidationError, inventory.deserialize, data)

    def test_find_inventory(self):
        """ Find an Inventory by ID """
        Inventory(name="tool", category="widget1", available=True).save()
        materials = Inventory(name="materials", category="widget2", available=False)
        materials.save()
        inventory = Inventory.find(materials.id)
        self.assertIsNot(inventory, None)
        self.assertEqual(inventory.id, inventory.id)
        self.assertEqual(inventory.name, "materials")
        self.assertEqual(inventory.available, False)

    def test_find_by_category(self):
        """ Find an Inventory by Category """
        Inventory(name="tools", category="widget1", available=True).save()
        Inventory(name="materials", category="widget2", available=False).save()
        inventorys = Inventory.find_by_category("widget1")
        self.assertEqual(inventorys[0].category, "widget1")
        self.assertEqual(inventorys[0].name, "tools")
        self.assertEqual(inventorys[0].available, True)

    def test_find_by_name(self):
        """ Find an inventory by Name """
        Inventory(name="tools", category="widget1", available=True).save()
        Inventory(name="materials", category="widget2", available=False).save()
        inventorys = Inventory.find_by_name("tools")
        self.assertEqual(inventorys[0].category, "widget1")
        self.assertEqual(inventorys[0].name, "tools")
        self.assertEqual(inventorys[0].available, True)

    def test_find_by_count(self):
        """ Find an inventory by Count """
        Inventory(name="tools", category="widget1", available=True, count = 1).save()
        Inventory(name="materials", category="widget2", available=False, count = 2).save()
        inventorys = Inventory.find_by_count(1)
        self.assertEqual(inventory[0].category, "widget1")
        self.assertEqual(inventory[0].name, "tools")
        self.assertEqual(inventory[0].available, True)
        self.assertEqual(inventory[0].count, 1)

    def test_find_by_condition(self):
        """ Find an inventory by Condition """
        Inventory(name="tools", category="widget1", available=True, condition="good").save()
        Inventory(name="materials", category="widget2", available=False, condition="bad").save()
        inventorys = Inventory.find_by_condition("good")
        self.assertEqual(inventory[0].category, "widget1")
        self.assertEqual(inventory[0].name, "tools")
        self.assertEqual(inventory[0].available, True)
        self.assertEqual(inventory[0].condition, "good")

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
