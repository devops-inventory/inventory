"""
Test Factory to make fake objects for testing
"""
import factory
from factory.fuzzy import FuzzyChoice
from app.models import Inventory

class InventoryFactory(factory.Factory):
    """ Creates fake inventory that you don't have to feed """
    class Meta:
        model = Inventory
    id = factory.Sequence(lambda n: n)
    name = factory.Faker('first_name')
    category = FuzzyChoice(choices=['widget1', 'widget2', 'widget3', 'widget4'])
    available = FuzzyChoice(choices=[True, False])

if __name__ == '__main__':
    for _ in range(10):
        inventory = InventoryFactory()
        print(inventory.serialize())

