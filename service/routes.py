######################################################################
# Copyright 2016, 2022 John J. Rofrano. All Rights Reserved.
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
######################################################################

# spell: ignore Rofrano jsonify restx dbname
"""
Product Store Service with UI
"""
from urllib.parse import quote_plus

from flask import url_for  # noqa: F401 pylint: disable=unused-import
from flask import abort, jsonify, request
from service.common import status  # HTTP Status Codes
from service.models import Category, Product

from . import app


######################################################################
# H E A L T H   C H E C K
######################################################################
@app.route("/health")
def healthcheck():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="OK"), status.HTTP_200_OK


######################################################################
# H O M E   P A G E
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


######################################################################
# C R E A T E   A   N E W   P R O D U C T
######################################################################
@app.route("/products", methods=["POST"])
def create_products():
    """
    Creates a Product
    This endpoint will create a Product based the data in the body that is posted
    """
    app.logger.info("Request to Create a Product...")
    check_content_type("application/json")

    data = request.get_json()
    app.logger.info("Processing: %s", data)
    product = Product()
    product.deserialize(data)
    product.create()
    app.logger.info("Product with new id [%s] saved!", product.id)

    message = product.serialize()

    location_url = url_for("get_products", product_id=product.id, _external=True)
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# L I S T   A L L   P R O D U C T S
######################################################################


@app.route(f"/products", methods=["GET"])
def list_products():
    """Return all products matching filter if provided."""
    app.logger.info("Request to list Products...")

    products: [Product] = []
    name = request.args.get(key="name")
    category = request.args.get(key="category")
    available = request.args.get(key="available")
    if name:  # filter by name
        app.logger.info("Find by name: %s", name)
        products = Product.find_by_name(name).all()
    elif category:
        app.logger.info("Find by category: %s", category)
        category_value = getattr(Category, category.upper())
        products = Product.find_by_category(category_value).all()
    elif available:
        app.logger.info("Find by available: %s", available)
        available_value = available.lower() in ["true", "yes", "1"]
        products = Product.find_by_availability(available_value).all()
    else:  # no filter
        app.logger.info("Find all")
        products = Product.all()
    if len(products) == 0:
        app.logger.error(f"No products found!")
        abort(
            status.HTTP_404_NOT_FOUND,
            f"No products found",
        )
    app.logger.info(f"Products returned: {len(products)}")
    return [p.serialize() for p in products], status.HTTP_200_OK


######################################################################
# R E A D   A   P R O D U C T
######################################################################
@app.route(f"/products/<int:product_id>", methods=["GET"])
def get_products(product_id: int):
    """Get product by ID.

    Args:
        product_id (int): ID of product to find.
    """
    found_product = Product.find(product_id)
    if not found_product:
        app.logger.error(f"Product not found for ID: {product_id}")
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Product with ID {product_id} not found",
        )
    app.logger.info("Returning product: %s", found_product.name)
    return found_product.serialize(), status.HTTP_200_OK


######################################################################
# U P D A T E   A   P R O D U C T
######################################################################


@app.route(f"/products/<int:product_id>", methods=["PUT"])
def update_products(product_id: int):
    """
    Update an Product
    This endpoint will update a Product based on the body that is posted
    """
    app.logger.info(f"Request to Update a product with id {product_id}")
    check_content_type("application/json")

    found_product = Product.find(product_id)
    if not found_product:
        app.logger.error(f"Product not found for ID: {product_id}")
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Product with ID {product_id} not found",
        )

    found_product.deserialize(data=request.get_json())
    found_product.id = product_id
    found_product.update()
    return found_product.serialize(), status.HTTP_200_OK


######################################################################
# D E L E T E   A   P R O D U C T
######################################################################


@app.route(f"/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id: int):
    """Delete the specified product by ID.

    Args:
        product_id (int): The ID of the product to delete
    """
    app.logger.info(f"Request to Delete a product with id {product_id}")

    found_product = Product.find(product_id)
    if not found_product:
        app.logger.error(f"Product not found for ID: {product_id}")
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Product with ID {product_id} not found",
        )
    found_product.delete()
    return "", status.HTTP_204_NO_CONTENT
