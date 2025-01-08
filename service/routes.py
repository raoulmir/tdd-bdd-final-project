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
from flask import jsonify, request, abort
from flask import url_for  # noqa: F401 pylint: disable=unused-import
from service.models import Product
from service.common import status  # HTTP Status Codes
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

    #
    # Uncomment this line of code once you implement READ A PRODUCT
    #
    # location_url = url_for("get_products", product_id=product.id, _external=True)
    location_url = "/"  # delete once READ is implemented
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# L I S T   A L L   P R O D U C T S
######################################################################

@app.route('/products', methods=['GET'])
def get_all_products():
    """Returns a list of Products"""
    app.logger.info("Request to list Products...")
    
    products = Product.all()

    app.logger.info(products)

    if len(products) < 1:
        abort(status.HTTP_404_NOT_FOUND)
    
    serialized_products = []
    for product in products:
        serialized_products.append(product.serialize())
        
    app.logger.info("Number of products: [%s]", len(serialized_products))

    return jsonify(serialized_products), status.HTTP_200_OK

@app.route('/products/name/', methods=['GET'])
def get_products_by_name():
    """Return a list of products that match the name provided"""
    app.logger.info("Request to list Products by name...")
    name = request.args.get("name")
    products = []

    if name:
        app.logger.info("Find by name: %s", name)
        products = Product.find_by_name(name)
    else:
        products = Product.all()
        app.logger.info("Find all")

    serialized_products = [product.serialize() for product in products]
        
    app.logger.info("Number of products with name [%s]: [%s]", name, len(serialized_products))

    return serialized_products, status.HTTP_200_OK


######################################################################
# R E A D   A   P R O D U C T
######################################################################

@app.route('/products/<product_id>', methods=['GET'])
def get_products(product_id):
    """
    Get a Product
    This endpoint will get a product based on the product_id provided in the query parameter
    """
    product = Product.find(product_id)

    location_url = url_for("get_products", product_id=product_id, _external=True)

    app.logger.info(product)

    if product is None:
        return jsonify("Product not found"), status.HTTP_404_NOT_FOUND, {"Location": location_url}

    product_id = product.id
    return jsonify(Product.serialize(product)), status.HTTP_200_OK, {"Location": location_url}


######################################################################
# U P D A T E   A   P R O D U C T
######################################################################

@app.route('/products/<product_id>', methods=['PUT'])
def update_products(product_id):
    """
    Update a Product
    This endpoint will update a Product based on the body that is posted
    """
    app.logger.info("Request to Update a product with id [%s]", product_id)
    check_content_type("application/json")

    product = Product.find(product_id)

    if product is None:
        abort(status.HTTP_404_NOT_FOUND)

    product.deserialize(data=request.get_json())

    product.update()

    location_url = url_for("update_products", product_id=product_id, _external=True)

    return jsonify(Product.serialize(product)), status.HTTP_200_OK, {"Location": location_url}


######################################################################
# D E L E T E   A   P R O D U C T
######################################################################

@app.route('/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    """
    Delete a product
    This endpoint will delete a product based on the product id provided in the query parameter
    """
    app.logger.info("Request to Delete a product with id [%s]", product_id)

    product = Product.find(product_id)

    if product is None:
        abort(status.HTTP_404_NOT_FOUND)

    location_url = url_for("update_products", product_id=product_id, _external=True)

    product.delete()

    return "", status.HTTP_204_NO_CONTENT, {"Location": location_url}