import json
import os
from sys import exc_info

from flask import Flask, abort, jsonify, request
from flask_cors import CORS
from sqlalchemy import exc

from .auth.auth import AuthError, get_token_auth_header, requires_auth
from .database.models import Drink, db_drop_and_create_all, setup_db

app = Flask(__name__)
setup_db(app)
CORS(app)

"""
@DONE uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
"""
db_drop_and_create_all()

# ROUTES
"""
@DONE implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks")
def get_drinks():
    try:
        drinks = Drink.query.all()
    except:
        abort(500)
    drink_list = []
    for drink in drinks:
        drink_list.append(drink.short())
    return jsonify({"success": True, "drinks": drink_list}), 200


"""
@DONE implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks-detail")
@requires_auth("get:drinks-detail")
def get_drinks_detail(payload):
    try:
        drinks = Drink.query.all()
    except:
        abort(500)
    drink_list = []
    for drink in drinks:
        drink_list.append(drink.long())
    return jsonify({"success": True, "drinks": drink_list}), 200


"""
@DONE implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def post_drinks(payload):
    try:
        body = request.get_json()
        title = body.get("title", None)
        recipe = body.get("recipe", None)
        if title is None or body is None:
            print(exc_info())
            abort(422)
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()
    except:
        print(exc_info())
        abort(400)
    return jsonify({"success": True, "drinks": [drink.long()]}), 200


"""
@DONE implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks/<int:id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def update_drink(payload, id):
    try:
        drink = Drink.query.get(id)
        if drink is None:
            abort(404)

        body = request.get_json()
        title = body.get("title", None)
        recipe = body.get("recipe", None)

        if title:
            drink.title = title
        else:
            drink.title = drink.title

        if recipe:
            drink.recipe = json.dumps(recipe)
        else:
            drink.recipe = json.dumps(drink.recipe)

        drink.insert()

        return jsonify({"success": True, "drinks": [drink.long()]}), 200

    except:
        print(exc_info())
        abort(400)


"""
@DONE implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks/<id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(payload, id):
    try:
        drink = Drink.query.get(id)
        if drink is None:
            abort(404)

        drink.delete()

        return jsonify({"success": True, "id": id})

    except:
        print(exc_info())
        abort(400)


# Error Handling
"""
Example error handling for unprocessable entity
"""


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({"success": False, "error": 422, "message": "unprocessable"}), 422


"""
@DONE implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

"""


@app.errorhandler(400)
def bad_request(error):
    return jsonify({"success": False, "error": 400, "message": "bad request"}), 400


@app.errorhandler(500)
def server_error(error):
    return jsonify({"success": False, "error": 500, "message": "internal server error"})


"""
@DONE implement error handler for 404
    error handler should conform to general task above
"""


@app.errorhandler(404)
def not_found(error):
    return (
        jsonify({"success": False, "error": 404, "message": "resource not found"}),
        404,
    )


"""
@DONE implement error handler for AuthError
    error handler should conform to general task above
"""


@app.errorhandler(AuthError)
def auth_error(error):
    body = error.error
    return (
        jsonify(
            {
                "success": False,
                "error": error.status_code,
                "message": body["description"],
            }
        ),
        error.status_code,
    )
