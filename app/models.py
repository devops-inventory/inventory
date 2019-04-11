# Copyright 2016, 2017 John Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Pet Model that uses Cloudant
You must initlaize this class before use by calling inititlize().
This class looks for an environment variable called VCAP_SERVICES
to get it's database credentials from. If it cannot find one, it
tries to connect to Cloudant on the localhost. If that fails it looks
for a server name 'cloudant' to connect to.
To use with Docker couchdb database use:
    docker run -d --name couchdb -p 5984:5984 -e COUCHDB_USER=admin -e COUCHDB_PASSWORD=pass couchdb
Docker Note:
    CouchDB uses /opt/couchdb/data to store its data, and is exposed as a volume
    e.g., to use current folder add: -v $(pwd):/opt/couchdb/data
    You can also use Docker volumes like this: -v couchdb_data:/opt/couchdb/data
Models for Inventory Service

All of the models are stored in this module

Models
------
Inventory - A SKU that is currently in stock by our e-commerce store

Attributes:
-----------
name(string) - the name of the product
category (string) - the category the product belongs to
(i.e., food, apparel, accessories, games, kitchenware)
available (boolean) - True for products that are currently in stock
condition (string) - The quality of the product's state (i.e. new, used, poor)
count (int) - The quantity in stock
"""
<<<<<<< HEAD

#pip install -r requirements.txt
import logging
import os
import json
from cloudant.client import Cloudant
from cloudant.query import Query
from requests import HTTPError, ConnectionError

# get configruation from enviuronment (12-factor)
ADMIN_PARTY = os.environ.get('ADMIN_PARTY', 'False').lower() == 'true'
CLOUDANT_HOST = os.environ.get('CLOUDANT_HOST', 'localhost')
CLOUDANT_USERNAME = os.environ.get('CLOUDANT_USERNAME', 'admin')
CLOUDANT_PASSWORD = os.environ.get('CLOUDANT_PASSWORD', 'pass')

class DataValidationError(Exception):
    """ Custom Exception with data validation fails """
    pass

class Inventory(object):
    """
    Inventory interface to database
    """
    logger = logging.getLogger(__name__)
    client = None   # cloudant.client.Cloudant
    database = None # cloudant.database.CloudantDatabase

    def __init__(self, name=None, category=None, available=True, condition=None, count=0):
        """ Constructor """
        self.id = None
        self.name = name
        self.category = category
        self.available = available
        self.condition = condition
        self.count = count

    def __repr__(self):
        return '<Inventory %r>' % (self.name)

    def create(self):
        """
        Creates a new inventory in the database
        """
        if self.name is None:   # name is the only required field
            raise DataValidationError('name attribute is not set')

        try:
            document = self.database.create_document(self.serialize())
        except HTTPError as err:
            Inventory.logger.warning('Create failed: %s', err)
            return

        if document.exists():
            self.id = document['_id']


    def create(self):
        """
        Creates a new Inventory in the database
        """
        if self.name is None:   # name is the only required field
            raise DataValidationError('name attribute is not set')

        try:
            document = self.database.create_document(self.serialize())
        except HTTPError as err:
            Inventory.logger.warning('Create failed: %s', err)
            return

        if document.exists():
            self.id = document['_id']


    def update(self):
        """
        Updates a Inventory in the database
        """
        try:
            document = self.database[self.id]
        except KeyError:
            document = None
        if document:
            document.update(self.serialize())
            document.save()

    def save(self):
        """ Saves a Pet in the database """
        if self.name is None:   # name is the only required field
            raise DataValidationError('name attribute is not set')
        if self.id:
            self.update()
        else:
            self.create()

    def delete(self):
        """ Deletes Inventory from the database """
        try:
            document = self.database[self.id]
        except KeyError:
            document = None
        if document:
            document.delete()
            
    def serialize(self):
        """ Serializes Inventory into a dictionary """
        return {"id": self.id,
                "name": self.name,
                "category": self.category,
                "available": self.available,
                "condition": self.condition,
                "count": self.count}

    def deserialize(self, data):
        """
        Deserializes Inventory from a dictionary

        Args:
            data (dict): A dictionary containing the Inventory data
        """
        try:
            self.name = data['name']
            self.category = data['category']
            self.available = data['available']
            self.condition = data['condition']
            self.count = data['count']
        except KeyError as error:
            raise DataValidationError('Invalid inventory: missing ' + error.args[0])
        except TypeError as error:
            raise DataValidationError('Invalid inventory: body of request contained' \
                                      'bad or no data')
        return self


    @classmethod
    def connect(cls):
        """ Connect to the server """
        cls.client.connect()

    @classmethod
    def disconnect(cls):
        """ Disconnect from the server """
        cls.client.disconnect()

    @classmethod
    def all(cls):
        """ Returns all of the Inventory in the database """
        cls.logger.info('Processing all Inventory')
        return cls.query.all()

    @classmethod
    def find(cls, inventory_id):
        """ Finds Inventory by it's ID """
        cls.logger.info('Processing lookup for id %s ...', inventory_id)
        return cls.query.get(inventory_id)

    @classmethod
    def find_or_404(cls, inventory_id):
        """ Find Inventory by it's id """
        cls.logger.info('Processing lookup or 404 for id %s ...', inventory_id)
        return cls.query.get_or_404(inventory_id)

    @classmethod
    def find_by_name(cls, name):
        """ Returns all Inventory with the given name

        Args:
            name (string): the name of the Inventory you want to match
        """
        cls.logger.info('Processing name query for %s ...', name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_category(cls, category):
        """ Returns all of the Inventory in a category

        Args:
            category (string): the category of the Inventory you want to match
        """
        cls.logger.info('Processing category query for %s ...', category)
        return cls.query.filter(cls.category == category)

    @classmethod
    def find_by_availability(cls, available=True):
        """ Query that finds Inventory by their availability """
        """ Returns Pets by their availability

        Args:
            available (boolean): True for inventorys that are available"""
        cls.logger.info('Processing available query for %s ...', available)
        return cls.query.filter(cls.available == available)

    @classmethod
    def find_by_condition(cls, condition):
        """ Returns all of the Inventory in a condition

        Args:
            condition (string): the condition of the Inventory you want to match
        """
        cls.logger.info('Processing condition query for %s ...', condition)
        return cls.query.filter(cls.condition == condition)


    @classmethod
    def find_by_count(cls, count):
        """ Returns all of the Inventory of a certain count

        Args:
            count (int): the count of the Inventory you want to match
        """
        cls.logger.info('Processing count query for %s ...', count)
        return cls.query.filter(cls.count == count)

############################################################
#  C L O U D A N T   D A T A B A S E   C O N N E C T I O N
############################################################

    @staticmethod
    def init_db(dbname='inventory'):
        """
        Initialized Cloundant database connection
        """
        opts = {}
        vcap_services = {}
        # Try and get VCAP from the environment or a file if developing
        if 'VCAP_SERVICES' in os.environ:
            Inventory.logger.info('Running in Bluemix mode.')
            vcap_services = json.loads(os.environ['VCAP_SERVICES'])
        # if VCAP_SERVICES isn't found, maybe we are running on Kubernetes?
        elif 'BINDING_CLOUDANT' in os.environ:
            Inventory.logger.info('Found Kubernetes Bindings')
            creds = json.loads(os.environ['BINDING_CLOUDANT'])
            vcap_services = {"cloudantNoSQLDB": [{"credentials": creds}]}
        else:
            Inventory.logger.info('VCAP_SERVICES and BINDING_CLOUDANT undefined.')
            creds = {
                "username": CLOUDANT_USERNAME,
                "password": CLOUDANT_PASSWORD,
                "host": CLOUDANT_HOST,
                "port": 5984,
                "url": "http://"+CLOUDANT_HOST+":5984/"
            }
            vcap_services = {"cloudantNoSQLDB": [{"credentials": creds}]}

        # Look for Cloudant in VCAP_SERVICES
        for service in vcap_services:
            if service.startswith('cloudantNoSQLDB'):
                cloudant_service = vcap_services[service][0]
                opts['username'] = cloudant_service['credentials']['username']
                opts['password'] = cloudant_service['credentials']['password']
                opts['host'] = cloudant_service['credentials']['host']
                opts['port'] = cloudant_service['credentials']['port']
                opts['url'] = cloudant_service['credentials']['url']

        if any(k not in opts for k in ('host', 'username', 'password', 'port', 'url')):
            Inventory.logger.info('Error - Failed to retrieve options. ' \
                             'Check that app is bound to a Cloudant service.')
            exit(-1)

        Inventory.logger.info('Cloudant Endpoint: %s', opts['url'])
        try:
            if ADMIN_PARTY:
                Inventory.logger.info('Running in Admin Party Mode...')
            Inventory.client = Cloudant(opts['username'],
                                  opts['password'],
                                  url=opts['url'],
                                  connect=True,
                                  auto_renew=True,
                                  admin_party=ADMIN_PARTY
                                 )
        except ConnectionError:
            raise AssertionError('Cloudant service could not be reached')

        # Create database if it doesn't exist
        try:
            Inventory.database = Inventory.client[dbname]
        except KeyError:
            # Create a database using an initialized client
            Inventory.database = Inventory.client.create_database(dbname)
        # check for success
        if not Inventory.database.exists():
            raise AssertionError('Database [{}] could not be obtained'.format(dbname))

