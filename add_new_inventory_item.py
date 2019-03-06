@app.route('/inventory', methods=['POST'])
def create_inventory_item():
    app.logger.info('Create inventory item requested')
    inventory_item = inventory_item()
    inventory_item.deserialize(request.get_json())
    inventory_item.save()
    app.logger.info('Created inventory item with id: {}'.format(inventory_item.id))
    return make_response(jsonify(inventory_item.serialize()),
                         status.HTTP_201_CREATED,
                         {'Location': url_for('get_inventory_item', inventory_item_id=inventory_item.id, _external=True)})


