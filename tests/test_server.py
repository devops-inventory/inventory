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
Pet API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN
"""

import mock
import unittest
import os
import logging
from flask_api import status    # HTTP Status Codes
#from mock import MagicMock, patch
from app.models import Inventory, DataValidationError, db
from .inventory_factory import InventoryFactory
import app.service as service

DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')

######################################################################
#  T E S T   C A S E S
######################################################################
class TestInventoryServer(unittest.TestCase):
    """ Inventory Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        service.app.debug = False
        service.initialize_logging(logging.INFO)
        # Set up the test database
        service.app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        """ Runs before each test """
        service.init_db()
        db.drop_all()    # clean up the last tests
        db.create_all()  # create new tables
        self.app = service.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def _create_inventorys(self, count):
        """ Factory method to create inventorys in bulk """
        inventorys = []
        for _ in range(count):
            test_inventory = InventoryFactory()
            resp = self.app.post('/inventory',
                                 json=test_inventory.serialize(),
                                 content_type='application/json')
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED, 'Could not create test inventory')
            new_inventory = resp.get_json()
            test_inventory.id = new_inventory['id']
            inventorys.append(test_inventory)
        return inventorys

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data['name'], 'Inventory REST API Service')

    def test_get_inventory_list(self):
        """ Get a list of Inventorys """
        self._create_inventorys(5)
        resp = self.app.get('/inventory')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_inventory(self):
        """ Get a single Inventory """
        # get the id of a inventory
        test_inventory = self._create_inventorys(1)[0]
        resp = self.app.get('/inventory/{}'.format(test_inventory.id),
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data['name'], test_inventory.name)

    def test_get_inventory_not_found(self):
        """ Get a Inventory thats not found """
        resp = self.app.get('/inventory/0')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_inventory(self):
        """ Create a new Inventory """
        test_inventory = InventoryFactory()
        resp = self.app.post('/inventory',
                             json=test_inventory.serialize(),
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertTrue(location != None)
        # Check the data is correct
        new_inventory = resp.get_json()
        self.assertEqual(new_inventory['name'], test_inventory.name, "Names do not match")
        self.assertEqual(new_inventory['category'], test_inventory.category, "Categories do not match")
        self.assertEqual(new_inventory['available'], test_inventory.available, "Availability does not match")
        self.assertEqual(new_inventory['condition'], test_inventory.condition, "Condition does not match")
        # Check that the location header was correct
        resp = self.app.get(location,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_inventory = resp.get_json()
        self.assertEqual(new_inventory['name'], test_inventory.name, "Names do not match")
        self.assertEqual(new_inventory['category'], test_inventory.category, "Categories do not match")
        self.assertEqual(new_inventory['available'], test_inventory.available, "Availability does not match")
        self.assertEqual(new_inventory['condition'], test_inventory.condition, "Condition does not match")

    def test_update_inventory(self):
        """ Update an existing Inventory """
        # create a inventory to update
        test_inventory = InventoryFactory()
        resp = self.app.post('/inventory',
                             json=test_inventory.serialize(),
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the inventory
        new_inventory = resp.get_json()
        new_inventory['category'] = 'unknown'
        resp = self.app.put('/inventory/{}'.format(new_inventory['id']),
                            json=new_inventory,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_inventory = resp.get_json()
        self.assertEqual(updated_inventory['category'], 'unknown')

    def test_delete_inventory(self):
        """ Delete a Inventory """
        test_inventory = self._create_inventorys(1)[0]
        resp = self.app.delete('/inventory/{}'.format(test_inventory.id),
                               content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get('/inventory/{}'.format(test_inventory.id),
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_inventory_list_by_category(self):
        """ Query Inventorys by Category """
        inventorys = self._create_inventorys(10)
        test_category = inventorys[0].category
        category_inventorys = [inventory for inventory in inventorys if inventory.category == test_category]
        resp = self.app.get('/inventory',
                            query_string='category={}'.format(test_category))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(category_inventorys))
        # check the data just to be sure
        for inventory in data:
            self.assertEqual(inventory['category'], test_category)

    @mock.patch('app.service.Inventory.find_by_name')
    def test_bad_request(self, bad_request_mock):
         """ Test a Bad Request error from Find By Name """
         bad_request_mock.side_effect = DataValidationError()
         resp = self.app.get('/inventory', query_string='name=widget1')
         self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch('app.service.Inventory.find_by_name')
    def test_method_not_supported(self, method_mock):
         """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
         method_mock.side_effect = None
         resp = self.app.put('/inventory', query_string='name=widget1')
         self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    @mock.patch('app.service.Inventory.find_by_name')
    def test_mediatype_not_supported(self, media_mock):
         """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
         media_mock.side_effect = DataValidationError()
         resp = self.app.post('/inventory', query_string='name=widget1')
         self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
         
    @mock.patch('app.service.Inventory.find_by_name')
    def test_search_bad_data(self, inventory_find_mock):
        """ Test a search that returns bad data """
        inventory_find_mock.return_value = None
        resp = self.app.get('/inventory', query_string='name=widget1')
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
