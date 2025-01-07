# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
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
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #

    def test_read_a_product(self):
        """It should retrieve a specified product from the database"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        result = product.find(product.id)
        self.assertEqual(result.name, product.name)
        self.assertEqual(result.description, product.description)
        self.assertEqual(Decimal(result.price), product.price)
        self.assertEqual(result.available, product.available)
        self.assertEqual(result.category, product.category)

    def test_update_a_product(self):
        """It should update an existing product"""
        updated_description = 'Update test description'

        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)

        product.description = updated_description
        product.update()
        updated_product = product.find(product.id)

        self.assertEqual(product.id, updated_product.id)
        self.assertEqual(updated_product.description, updated_description)

        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, product.id)
        self.assertEqual(products[0].description, updated_description)

    def test_update_a_product_failure(self):
        """It should fail approriately when updating product with a non-existing ID"""
        updated_description = 'Update test description'

        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)

        product.description = updated_description
        product.id = None

        with self.assertRaises(DataValidationError):
            product.update()

    def test_delete_a_product(self):
        """It should delete a specified existing product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)

        products = Product.all()
        self.assertEqual(len(products), 1)

        product.delete()
        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_list_all_products(self):
        """It should list all the products in the database"""
        self.assertEqual(len(Product.all()), 0)

        for product in range(5):
            product = ProductFactory()
            product.create()

        self.assertEqual(len(Product.all()), 5)

    def test_find_product_by_name(self):
        """It should find a product specified by the name"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()

        name = products[0].name

        hits = [hit for hit in Product.all() if name in hit.name]
        count = len(hits)

        search = Product.find_by_name(name)

        self.assertEqual(len(list(search)), count)

        for result in search:
            self.assertEqual(name, result.name)

    def test_find_product_by_availability(self):
        """It should find a product by specified availability"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        availability = products[0].available

        hits = [hit for hit in Product.all() if availability is hit.available]
        count = len(hits)

        search = Product.find_by_availability(availability)

        self.assertEqual(len(list(search)), count)

        for result in search:
            self.assertEqual(availability, result.available)

    def test_find_product_by_category(self):
        """It should find product by specified category"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        category = products[0].category
        hits = [hit for hit in Product.all() if category is hit.category]
        count = len(hits)

        search = Product.find_by_category(category)

        self.assertEqual(len(list(search)), count)

        for result in search:
            self.assertEqual(category, result.category)

    def test_deserialize_product_from_dict(self):
        """It should deserialize dictionary of product"""
        product = ProductFactory()
        product.id = None
        dictionary = product.serialize()
        self.assertIsInstance(dictionary, dict)
        self.assertIsInstance(product.deserialize(dictionary), Product)

    def test_deserialize_from_object(self):
        """It should raise a data validation exception when trying to deserialize instance of Product"""
        product = ProductFactory()
        product.id = None
        with self.assertRaises(DataValidationError):
            self.assertRaises(TypeError, product.deserialize, product)

    def test_deserialize_from_product_with_missing_key(self):
        """It should raise a data validation exception when the price field is missing"""
        product = ProductFactory()
        product.id = None
        dictionary = product.serialize()
        del(dictionary['price'])
        with self.assertRaises(DataValidationError):
            self.assertRaises(KeyError, product.deserialize, dictionary)

    def test_deserialize_product_with_attribute_error(self):
        """It should raise a data validation exception when the 'category' is set to one not defined by enum"""
        product = ProductFactory()
        product.id = None
        dictionary = product.serialize()
        self.assertIsInstance(dictionary, dict)
        dictionary['category'] = 'MACHINE'
        with self.assertRaises(DataValidationError):
            self.assertRaises(AttributeError, product.deserialize, dictionary)

    def test_deserialize_product_with_invalid_availability(self):
        """It should raise a data validation exception when availability value is of wrong data type"""
        product = ProductFactory()
        product.id = None
        dictionary = product.serialize()
        self.assertIsInstance(dictionary, dict)
        dictionary['available'] = 'SUPERPOSITION'
        with self.assertRaises(DataValidationError):
            product.deserialize(dictionary)