# Copyright 2016, 2017 John J. Rofrano. All Rights Reserved. JD.
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
Inventory Service

Paths:
------
GET /inventory - Returns a list all of the Inventory
GET /inventory/{id} - Returns the Inventory with a given id number
POST /inventory - creates a new Inventory record in the database
PUT /inventory/{id} - updates an Inventory record in the database
PUT /inventory/{id}/void - voids Inventory record in the database
DELETE /inventory/{id} - deletes an Inventory record in the database
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import NotFound

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from cloudant.client import Cloudant
from cloudant.query import Query
from app.models import Inventory, DataValidationError

# Import Flask application
from . import app

######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)

@app.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
    """ Handles bad requests with 400_BAD_REQUEST """
    message = error.message or str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_400_BAD_REQUEST,
                   error='Bad Request',
                   message=message), status.HTTP_400_BAD_REQUEST

@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """ Handles resources not found with 404_NOT_FOUND """
    message = error.message or str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_404_NOT_FOUND,
                   error='Not Found',
                   message=message), status.HTTP_404_NOT_FOUND

@app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
def method_not_supported(error):
    """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
    message = error.message or str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_405_METHOD_NOT_ALLOWED,
                   error='Method not Allowed',
                   message=message), status.HTTP_405_METHOD_NOT_ALLOWED

#@app.errorhandler(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
#def mediatype_not_supported(error):
#    """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
#    message = error.message or str(error)
#    app.logger.warning(message)
#    return jsonify(status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
#                   error='Unsupported media type',
#                   message=message), status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """ Handles unexpected server error with 500_SERVER_ERROR """
    message = error.message or str(error)
    app.logger.error(message)
    return jsonify(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                   error='Internal Server Error',
                   message=message), status.HTTP_500_INTERNAL_SERVER_ERROR


######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    """ Root URL response """
    #return jsonify(name='Inventory REST API Service',
                   #version='1.0',
                   #paths=url_for('list_inventory', _external=True)
                  #), status.HTTP_200_OK
    return app.send_static_file('mine_index.html')

######################################################################
# MAKE INVENTORY VOID
######################################################################
@app.route('/inventory/<string:inventory_id>/void', methods=['PUT'])
def void_inventory(inventory_id):
    """Void an inventory item"""
    app.logger.info('Request to void inventory with id: %s', inventory_id)
    check_content_type('application/json')
    inventory = Inventory.find(inventory_id)
    if not inventory:
        raise NotFound("Inventory with id '{}' was not found.".format(inventory_id))
    data = request.get_json()
    app.logger.info(data)
    inventory.deserialize(data)
    inventory.id = inventory_id
    inventory.available = False
    inventory.save()
    return make_response(jsonify(inventory.serialize()), status.HTTP_200_OK)

######################################################################
# LIST ALL INVENTORY
######################################################################
@app.route('/inventory', methods=['GET'])
def list_inventory():
    """ Returns all of the Inventory """
    app.logger.info('Request for inventory list')
    inventory = []
    category = request.args.get('category')
    name = request.args.get('name')
    condition = request.args.get('condition')
    count = request.args.get('count')
    available = request.args.get('available')
    if category:
        inventory = Inventory.find_by_category(category)
    elif name:
        inventory = Inventory.find_by_name(name)
    else:
        inventory = Inventory.all()

    results = [inventory.serialize() for inventory in inventory]
    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# RETRIEVE INVENTORY
######################################################################
@app.route('/inventory/<string:inventory_id>', methods=['GET'])
def get_inventory(inventory_id):
    """
    Retrieve a single Inventory

    This endpoint will return an Inventory based on it's id
    """
    app.logger.info('Request for Inventory with id: %s', inventory_id)
    inventory = Inventory.find(inventory_id)
    if not inventory:
        raise NotFound("Inventory with id '{}' was not found.".format(inventory_id))
    return make_response(jsonify(inventory.serialize()), status.HTTP_200_OK)


######################################################################
# ADD NEW INVENTORY
######################################################################
@app.route('/inventory', methods=['POST'])
def create_inventory():
    """
    Creates Inventory
    This endpoint will create Inventory based the data in the body that is posted
    """
    data ={}
    # Check for form submission data
    if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
        app.logger.info('Getting data from form submit')
        data = {
            'name': request.form['name'],
            'category': request.form['category'],
            'available': request.form['available']==True,
            'condition': request.form['condition'],
            'count': request.form['count']
        }
    else:
        app.logger.info('Getting data from API call')
        data = request.get_json()
    app.logger.info(data)
    inventory = Inventory()
    inventory.deserialize(data)
    inventory.save()
    message = inventory.serialize()
    location_url = url_for('get_inventory', inventory_id=inventory.id, _external=True)
    return make_response(jsonify(message), status.HTTP_201_CREATED,
                         {'Location': location_url})


######################################################################
# UPDATE AN EXISTING INVENTORY
######################################################################
@app.route('/inventory/<string:inventory_id>', methods=['PUT'])
def update_inventory(inventory_id):
    """
    Update a Inventory

    This endpoint will update an Inventory based the body that is posted
    """
    app.logger.info('Request to Update a inventory with id [%s]', inventory_id)
    check_content_type('application/json')
    inventory = Inventory.find(inventory_id)
    if not inventory:
        raise NotFound("inventory with id '{}' was not found.".format(inventory_id))
    data = request.get_json()
    app.logger.info(data)
    inventory.deserialize(data)
    inventory.id = inventory_id
    inventory.save()
    return make_response(jsonify(inventory.serialize()), status.HTTP_200_OK)

######################################################################
# DELETE INVENTORY
######################################################################
@app.route('/inventory/<string:inventory_id>', methods=['DELETE'])
def delete_inventory(inventory_id):
    """
    Delete an Inventory

    This endpoint will delete an inventory based the id specified in the path
    """
    app.logger.info('Request to delete inventory with id: %s', inventory_id)
    inventory = Inventory.find(inventory_id)
    if inventory:
        inventory.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
# DELETE ALL PET DATA (for testing only)
######################################################################
@app.route('/inventory/reset', methods=['DELETE'])
def inventory_reset():
    """ Removes all inventory from the database """
    Inventory.remove_all()
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def init_db():
    """ Initialies the Cloudant app """
    global app
    Inventory.init_db(app)

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers['Content-Type'] == content_type:
        return
    app.logger.error('Invalid Content-Type: %s', request.headers['Content-Type'])
    abort(415, 'Content-Type must be {}'.format(content_type))
