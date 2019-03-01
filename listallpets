# Pull options from environment
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('PORT', '5000')
HOST = os.getenv('HOST', '0.0.0.0')
#. . . CODE HERE . . .
if __name__ == "__main__":
 app.run(host=HOST, port=int(PORT), debug=DEBUG)

@app.route('/')
def index():
  return jsonify(name='Inventory Demo REST API Service',
  version='1.0',
  url=url_for('list_inventory', _external=True)), status.HTTP_200_OK

@app.route('/pets', methods=['GET'])
def list_inventory():
  results = []
  category = request.args.get('category')
  if category:
    app.logger.info('Getting Inventory for category: {}'.format(category))
    results = Inventory.find_by_category(category)
  else:
    app.logger.info('Getting all Pets')
    results = Inventory.all()
 return jsonify([Inventory.serialize() for pet in results]), status.HTTP_200_OK
