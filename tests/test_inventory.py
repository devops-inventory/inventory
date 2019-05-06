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
from mock import MagicMock, patch
from requests import HTTPError, ConnectionError
import os
import json
import logging
from app.models import Inventory, DataValidationError
from app import app

VCAP_SERVICES = {
    'cloudantNoSQLDB': [
        {'credentials': {
            'username': 'admin',
            'password': 'pass',
            'host': 'localhost',
            'port': 5984,
            'url': 'http://admin:pass@localhost:5984'
            }
        }
    ]
}


######################################################################
#  T E S T   C A S E S
######################################################################
class TestInventory(unittest.TestCase):
    """ Test Cases for Inventory """        

    def setUp(self):
        Inventory.init_db("test")
        Inventory.remove_all()
        
    def test_create_a_inventory(self):
        """ Create inventory and assert that it exists """
        inventory = Inventory(name="tools", category="widget1", available=True, condition="new")
        self.assertNotEqual(inventory, None)
        self.assertEqual(inventory.id, None)
        self.assertEqual(inventory.name, "tools")
        self.assertEqual(inventory.category, "widget1")
        self.assertEqual(inventory.available, True)
        self.assertEqual(inventory.condition, "new")

    def test_add_a_inventory(self):
        """ Create an inventory and add it to the database """
        inventorys = Inventory.all()
        self.assertEqual(inventorys, [])
        inventory = Inventory(name="tools", category="widget1", available=True, condition="new")
        self.assertTrue(inventory != None)
        self.assertEqual(inventory.id, None)
        inventory.save()
        # Asert that it was assigned an id and shows up in the database
        self.assertNotEqual(inventory.id, None)
        inventorys = Inventory.all()
        self.assertEqual(len(inventorys), 1)
        self.assertEqual(inventorys[0].name, "tools")
        self.assertEqual(inventorys[0].category, "widget1")
        self.assertEqual(inventorys[0].available, True)
        self.assertEqual(inventorys[0].condition, "new")

    def test_update_a_inventory(self):
        """ Update an Inventory """
        inventory = Inventory(name="tools", category="widget1", available=True,condition="new")
        inventory.save()
        self.assertNotEqual(inventory.id, None)
        # Change it an save it
        inventory.category = "jkwidget2"
        inventory.save()
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        inventory = Inventory.all()
        self.assertEqual(len(inventory), 1)
        self.assertEqual(inventory[0].category, "jkwidget2")
        self.assertEqual(inventory[0].name, "tools")

    def test_delete_a_inventory(self):
        """ Delete an inventory """
        inventory = Inventory(name="tools", category="widget1", available=True,condition="new")
        inventory.save()
        self.assertEqual(len(Inventory.all()), 1)
        # delete the inventory and make sure it isn't in the database
        inventory.delete()
        self.assertEqual(len(Inventory.all()), 0)

    def test_serialize_a_inventory(self):
        """ Test serialization of a Inventory """
        inventory = Inventory(name="tools", category="widget1", available=False, condition="new")
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
        self.assertIn('condition', data)
        self.assertEqual(data['condition'], "new")

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

    @patch('cloudant.database.CloudantDatabase.__getitem__')
    def test_deserialize_bad_data1(self, bad_mock):
        """ Test deserialization of bad data """
        data = "this is not a dictionary"
        bad_mock.side_effect = KeyError()
        data = {}
        inventory = Inventory()
        bad_mock.side_effect = DataValidationError()
        self.assertRaises(DataValidationError, inventory.deserialize,data)
        
    @patch('cloudant.database.CloudantDatabase.__getitem__')
    def test_deserialize_bad_data2(self, bad_mock):
        """ Test deserialization of bad data """
        data = "this is not a dictionary"
        bad_mock.side_effect = TypeError()
        data = {"id": 1, "name": "materials", "category": "widget2", "available": True, "count":1,"condition":"new"}
        inventory = Inventory()
        inventory.deserialize(data)

    def test_find_inventory(self):
        """ Find an Inventory by ID """
        Inventory("tools", "widget1").save()
        # saved_pet = Pet("kitty", "cat").save()
        saved_inventory = Inventory("materials", "widget2")
        saved_inventory.save()
        inventory = Inventory.find(saved_inventory.id)
        self.assertIsNot(inventory, None)
        self.assertEqual(inventory.id, saved_inventory.id)
        self.assertEqual(inventory.name, "materials")

    def test_find_by_category(self):
        """ Find an Inventory by Category """
        Inventory(name="tools", category="widget1", available=True,condition="new").save()
        Inventory(name="materials", category="widget2", available=False,condition="old").save()
        inventory = Inventory.find_by_category("widget1")
        self.assertEqual(inventory[0].category, "widget1")
        self.assertEqual(inventory[0].name, "tools")
        self.assertEqual(inventory[0].available, True)
        self.assertEqual(inventory[0].condition, "new")


    def test_find_by_name(self):
        """ Find an inventory by Name """
        Inventory(name="tools", category="widget1", available=True).save()
        Inventory(name="materials", category="widget2", available=False).save()
        inventory = Inventory.find_by_name("tools")
        self.assertEqual(inventory[0].category, "widget1")
        self.assertEqual(inventory[0].name, "tools")
        self.assertEqual(inventory[0].available, True)


    def test_find_by_condition(self):
        """ Find an inventory by Condition """
        Inventory(name="tools", category="widget1", available=True, condition="new").save()
        Inventory(name="materials", category="widget2", available=False, condition="old").save()
        inventory = Inventory.find_by_condition("new")
        self.assertNotEqual(len(inventory), 0)
        self.assertEqual(inventory[0].category, "widget1")
        self.assertEqual(inventory[0].name, "tools")
        self.assertEqual(inventory[0].available, True)
        self.assertEqual(inventory[0].condition, "new")
        
    def test_find_by_availability(self):
        """ Find an inventory by Condition """
        Inventory(name="tools", category="widget1", available=True, condition="new").save()
        Inventory(name="materials", category="widget2", available=False, condition="old").save()
        inventory = Inventory.find_by_availability(True)
        self.assertNotEqual(len(inventory), 0)
        self.assertEqual(inventory[0].category, "widget1")
        self.assertEqual(inventory[0].name, "tools")
        self.assertEqual(inventory[0].available, True)
        self.assertEqual(inventory[0].condition, "new")

    def test_create_query_index(self):
        """ Test create query index """
        Inventory("tools", "widget1", False, "new").save()
        Inventory("materials", "widget2", True, "old").save()
        Inventory.create_query_index('category')

    def test_connect(self):
        """ Test Connect """
        Inventory.connect()
        inventory = Inventory("tools", "widget1", False, "new")
        self.assertNotEqual(AttributeError, inventory.save)
        
    def test_disconnect(self):
        """ Test Disconnect """
        Inventory.disconnect()
        inventory = Inventory("tools", "widget1", False, "new")
        self.assertRaises(AttributeError, inventory.save)

    @patch('cloudant.database.CloudantDatabase.create_document')
    def test_noname_error(self, bad_mock):
        """ Test an inventory without name error """
        bad_mock.side_effect = DataValidationError()
        inventory = Inventory(None, "widget1", False, "new")
        self.assertRaises(DataValidationError, inventory.create)

    @patch('cloudant.database.CloudantDatabase.create_document')
    def test_http_error(self, bad_mock):
        """ Test a Bad Create with HTTP error """
        bad_mock.side_effect = HTTPError()
        inventory = Inventory("tools", "widget1", False, "new")
        inventory.create()
        self.assertIsNone(inventory.id)    

    @patch('cloudant.document.Document.exists')
    def test_document_not_exist(self, bad_mock):
        """ Test a Bad Document Exists """
        bad_mock.return_value = False
        inventory = Inventory("tools", "widget1", False, "new")
        inventory.create()
        self.assertIsNone(inventory.id)

    @patch('cloudant.database.CloudantDatabase.__getitem__')
    def test_key_error_on_update(self, bad_mock):
        """ Test KeyError on update """
        bad_mock.side_effect = KeyError()
        inventory = Inventory("tools", "widget1", False, "new")
        inventory.save()
        inventory.name = 'Wrench'
        inventory.update()
        #self.assertEqual(pet.name, 'fido')

    @patch('cloudant.database.CloudantDatabase.__getitem__')
    def test_key_error_on_delete(self, bad_mock):
        """ Test KeyError on delete """
        bad_mock.side_effect = KeyError()
        inventory = Inventory("tools", "widget1", False, "new")
        inventory.create()
        inventory.delete()
        
    @patch('cloudant.client.Cloudant.__init__')
    def test_connection_error(self, bad_mock):
        """ Test Connection error handler """
        bad_mock.side_effect = ConnectionError()
        self.assertRaises(AssertionError, Inventory.init_db, 'test')

    @patch('cloudant.client.Cloudant.__init__')
    def test_exist_error(self, bad_mock):
        """ Test DB Exist error handler """
        bad_mock.side_effect = AssertionError()
        resp = Inventory.database.exists()
        self.assertNotEqual(AssertionError, Inventory.database.exists(), 'test')

  #  @patch.dict(os.environ, {'VCAP_SERVICES': json.dumps(VCAP_SERVICES)})
   # def test_vcap_services(self):
    #    """ Test if VCAP_SERVICES works """
     #   Inventory.init_db()
      #  self.assertIsNotNone(Inventory.client)
       # Inventory("tools", "widget1", True, "new").save()
        #inventorys = Inventory.find_by_name("tools")
        #self.assertNotEqual(len(inventorys), 0)
        #self.assertEqual(inventorys[0].name, "tools")    

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
