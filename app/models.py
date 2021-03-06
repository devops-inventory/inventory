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
Inventory Model that uses Cloudant
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

#pip install -r requirements.txt
import logging
import os
import json
from retry import retry
from cloudant.client import Cloudant
from cloudant.query import Query
from requests import HTTPError, ConnectionError

# get configruation from enviuronment (12-factor)
ADMIN_PARTY = os.environ.get('ADMIN_PARTY', 'False').lower() == 'true'
CLOUDANT_HOST = os.environ.get('CLOUDANT_HOST', 'localhost')
CLOUDANT_USERNAME = os.environ.get('CLOUDANT_USERNAME', 'admin')
CLOUDANT_PASSWORD = os.environ.get('CLOUDANT_PASSWORD', 'pass')

# global variables for retry (must be int)
RETRY_COUNT = int(os.environ.get('RETRY_COUNT', 15))
RETRY_DELAY = int(os.environ.get('RETRY_DELAY', 3))
RETRY_BACKOFF = int(os.environ.get('RETRY_BACKOFF', 2))

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

    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF, tries=RETRY_COUNT,
           logger=logger)
    def create(self):
        """Creates a new inventory in the database"""
        if self.name is None:   # name is the only required field
            raise DataValidationError('name attribute is not set')
        try:
            document = self.database.create_document(self.serialize())
        except HTTPError as err:
            Inventory.logger.warning('Create failed: %s', err)
            return

        if document.exists():
            self.id = document['_id']
    
    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF, tries=RETRY_COUNT,
           logger=logger)
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
    
    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF, tries=RETRY_COUNT,
           logger=logger)
    def save(self):
        """ Saves a Inventory in the database """
        if self.name is None:   # name is the only required field
            raise DataValidationError('name attribute is not set')
        if self.id:
            self.update()
        else:
            self.create()
    
    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF, tries=RETRY_COUNT,
           logger=logger)
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
        if not self.id and '_id' in data:
            self.id = data['_id']

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
    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF, tries=RETRY_COUNT,
           logger=logger)
    def create_query_index(cls, field_name, order='asc'):
        """ Creates a new query index for searching """
        cls.database.create_query_index(index_name=field_name, fields=[{field_name: order}])

    @classmethod
    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF, tries=RETRY_COUNT,
           logger=logger)
    def all(cls):
        """ Returns all of the Inventory in the database """
        return cls.query.all()

    @classmethod
    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF, tries=RETRY_COUNT,
           logger=logger)
    def remove_all(cls):
        """ Removes all documents from the database (use for testing)  """
        for document in cls.database:
            document.delete()

    @classmethod
    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF, tries=RETRY_COUNT,
           logger=logger)
    def all(cls):
        """ Query that returns all inventory """
        results = []
        for doc in cls.database:
            inventory = Inventory().deserialize(doc)
            inventory.id = doc['_id']
            results.append(inventory)
        return results

    @classmethod
    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF, tries=RETRY_COUNT,
           logger=logger)
    def find_by(cls, **kwargs):
        """ Find records using selector """
        query = Query(cls.database, selector=kwargs)
        results = []
        for doc in query.result:
            inventory = Inventory()
            inventory.deserialize(doc)
            results.append(inventory)
        return results

    @classmethod
    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF, tries=RETRY_COUNT,
           logger=logger)
    def find(cls, inventory_id):
        """ Query that finds Inventory by their id """
        try:
            document = cls.database[inventory_id]
            return Inventory().deserialize(document)
        except KeyError:
            return None

    @classmethod
    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF, tries=RETRY_COUNT,
           logger=logger)
    def find_by_name(cls, name):
        """ Query that finds Inventory by their name """
        return cls.find_by(name=name)

    @classmethod
    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF, tries=RETRY_COUNT,
           logger=logger)
    def find_by_category(cls, category):
        """ Query that finds Inventory by their category """
        return cls.find_by(category=category)

    @classmethod
    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF, tries=RETRY_COUNT,
           logger=logger)
    def find_by_availability(cls, available=True):
        """ Query that finds Inventory by their availability """
        return cls.find_by(available=available)

    @classmethod
    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF, tries=RETRY_COUNT,
           logger=logger)
    def find_by_condition(cls, condition):
        """ Query that finds Inventory by their condition """
        return cls.find_by(condition=condition)


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
        if 'BINDING_CLOUDANT' in os.environ:
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
