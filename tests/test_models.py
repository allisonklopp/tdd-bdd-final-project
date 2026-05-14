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
import logging
import os
import unittest
from decimal import Decimal
from itertools import product

from service import app
from service.models import Category, Product, db
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
        product = Product(
            name="Fedora",
            description="A red hat",
            price=12.50,
            available=True,
            category=Category.CLOTHS,
        )
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

    def test_read_a_product(self):
        """Read a product."""
        product = ProductFactory()
        logging.info(f"Read Product : {product}")
        product.id = None
        product.create()

        self.assertIsNotNone(product.id)
        found_product = Product.find(product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(Decimal(found_product.price), product.price)
        self.assertEqual(found_product.available, product.available)
        self.assertEqual(found_product.category, product.category)

    def test_update_a_product(self):
        """Update a product."""
        product = ProductFactory()
        logging.info(f"Update Product : {product}")
        product.id = None
        product.create()

        logging.info(f"Product before changes: {product}")
        product.description = "Some OTHER description"
        original_id = product.id
        product.update()

        updated_product = Product.find(product.id)
        self.assertNotEqual(updated_product.id, None)
        self.assertEqual(updated_product.description, "Some OTHER description")

        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, original_id)
        self.assertEqual(products[0].description, "Some OTHER description")

    def test_delete_a_product(self):
        """Delete a product."""
        product = ProductFactory()
        logging.info(f"Delete Product : {product}")
        product.id = None
        product.create()

        self.assertEqual(len(Product.all()), 1)
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """List all products."""
        products = Product.all()
        self.assertEqual(products, [])
        products = ProductFactory.create_batch(5)
        for p in products:
            p.create()
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_search_product_by_name(self):
        """Search for a product by name"""
        products = ProductFactory.create_batch(5)
        for p in products:
            p.create()
        first_product = Product.all()[0]
        count: int = 0
        for p in Product.all():
            if first_product.name == p.name:
                count += 1
        found_products = Product.find_by_name(first_product.name)
        self.assertEqual(found_products.count(), count)
        for p in found_products:
            self.assertEqual(p.name, first_product.name)

    def test_search_product_by_category(self):
        """Search for a product by category"""
        products = ProductFactory.create_batch(10)
        for p in products:
            p.create()

        first_category = Product.all()[0].category

        count = len([a for a in Product.all() if a.category == first_category])

        found_products = Product.find_by_category(first_category)

        self.assertEqual(found_products.count(), count)

        for item in found_products:
            self.assertEqual(item.category, first_category)

    def test_search_product_by_availability(self):
        """Search for a product by availability"""
        products = ProductFactory.create_batch(10)
        for p in products:
            p.create()

        first_availability = Product.all()[0].available
        count = len([a for a in Product.all() if a.available == first_availability])
        found_products = Product.find_by_availability(first_availability)
        self.assertEqual(found_products.count(), count)

        for p in found_products:
            self.assertEqual(p.available, first_availability)
