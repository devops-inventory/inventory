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
Inventory API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN
"""

import mock
import unittest
import os
import json
import logging
from flask_api import status    # HTTP Status Codes
#from mock import MagicMock, patch
from app.models import Inventory, DataValidationError
from .inventory_factory import InventoryFactory
import app.service as app

######################################################################
#  T E S T   C A S E S
######################################################################
class TestInventoryServer(unittest.TestCase):
    """ Inventory Server Tests """

    def setUp(self):
        """ Runs before each test """
        """ Initialize the Cloudant database """
        self.app = app.app.test_client()
        Inventory.init_db("tests_intentory")
        Inventory.remove_all()
        Inventory("tools", "widget1", True, "new",1).save()
        Inventory("materials", "widget2", False, "old",2).save()

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
        self.assertIn('Inventory Demo REST API Service', resp.data)

    def test_get_inventory_list(self):
        """ Get a list of Inventorys """
        resp = self.app.get('/inventory')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)

    def test_get_inventory(self):
        """ Get a single Inventory """
        inventory = self.get_inventory('tools')[0] # returns a list
        resp = self.app.get('/inventory/{}'.format(inventory['id']))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['name'], 'tools')

    def test_get_inventory_not_found(self):
        """ Get a Inventory thats not found """
        resp = self.app.get('/inventory/0')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = json.loads(resp.data)
        self.assertIn('was not found', data['message'])

    def test_create_inventory(self):
        """ Create a new inventory """
        # save the current number of inventory for later comparrison
        inventory_count = self.get_inventory_count()
        # add a new inventory
        new_inventory = {'name': 'tools', 'category': 'widget1', 'available': True, 'condition': 'new','count':1}
        data = json.dumps(new_inventory)
        resp = self.app.post('/inventory', data=data, content_type='application/json')
        # if resp.status_code == 429: # rate limit exceeded
        #     sleep(1)                # wait for 1 second and try again
        #     resp = self.app.post('/inventory', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertNotEqual(location, None)
        # Check the data is correct
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['name'], 'tools')
        # check that count has gone up and includes tool
        resp = self.app.get('/inventory')
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), inventory_count + 1)
        self.assertIn(new_json, data)

    def test_void_inventory(self):
        """ VOID Inventory """
        inventory = self.get_inventory('tools')[0] # returns a list
        self.assertEqual(inventory['available'], True)
        inventory['available'] = False
        # make the call
        data = json.dumps(inventory)
        resp = self.app.put('/inventory/{}/void'.format(inventory['id']), data=data,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # go back and get it again
        resp = self.app.get('/inventory/{}'.format(inventory['id']), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['available'], False)

    def test_void_non_existing_inventory(self):
        """ Void inventory that doesn't exist """
        resp = self.app.put('/inventory/0/void', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_inventory(self):
        """ Update an existing Inventory """
        inventory = self.get_inventory('tools')[0] # returns a list
        self.assertEqual(inventory['category'], 'widget1')
        inventory['category'] = 'widget3'
        # make the call
        data = json.dumps(inventory)
        resp = self.app.put('/inventory/{}'.format(inventory['id']), data=data,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # go back and get it again
        resp = self.app.get('/inventory/{}'.format(inventory['id']), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['category'], 'widget3')

    def test_delete_inventory(self):
        """ Delete a Inventory """
        inventory = self.get_inventory('tools')[0] # returns a list
        inventory_count = self.get_inventory_count()
        resp = self.app.delete('/inventory/{}'.format(inventory['id']),
                               content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        new_count = self.get_inventory_count()
        self.assertEqual(new_count, inventory_count - 1)

    def test_inventory_reset(self):
        """ Removes all inventory from the database """
        resp = self.app.delete('/inventory/reset')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_query_inventory_list_by_category(self):
        """ Query Inventorys by Category """
        resp = self.app.get('/inventory', query_string='category=widget1')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)
        self.assertIn('tools', resp.data)
        self.assertNotIn('materials', resp.data)
        data = json.loads(resp.data)
        query_item = data[0]
        self.assertEqual(query_item['category'], 'widget1')

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


#    @mock.patch('app.service.Inventory.find_by_name')
#    def test_mediatype_not_supported(self, media_mock):
#         """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
#         media_mock.side_effect = DataValidationError()
#         resp = self.app.post('/inventory', query_string='name=widget1', content_type='application/pdf')
#         self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    @mock.patch('app.service.Inventory.find_by_name')
    def test_search_bad_data(self, inventory_find_mock):
        """ Test a search that returns bad data """
        inventory_find_mock.return_value = None
        resp = self.app.get('/inventory', query_string='name=widget1')
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


######################################################################
# Utility functions
######################################################################

    def get_inventory(self, name):
        """ retrieves a inventory for use in other actions """
        resp = self.app.get('/inventory',
                            query_string='name={}'.format(name))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreater(len(resp.data), 0)
        self.assertIn(name, resp.data)
        data = json.loads(resp.data)
        return data

    def get_inventory_count(self):
        """ save the current number of inventory """
        resp = self.app.get('/inventory')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        return len(data)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
