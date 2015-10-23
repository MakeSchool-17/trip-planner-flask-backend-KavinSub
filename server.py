from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
from pymongo import MongoClient
from bson.objectid import ObjectId
from utils.mongo_json_encoder import JSONEncoder
import bcrypt
from functools import wraps

# Basic Setup
app = Flask(__name__)
mongo = MongoClient('localhost', 27017)
app.db = mongo.develop_database
api = Api(app)

def check_auth(username, password):
    #return username == 'admin' and password == 'secret'
    user_collection = app.db.users
    user = user_collection.find_one({'user': username})

    if user is None:
        return False
    else:
        pass_encoded = password.encode('utf-8')
        validated = (bcrypt.hashpw(pass_encoded, user['pass']) == user['pass'])
        return validated


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            message = {'error': 'Basic Auth Required.'}
            resp = jsonify(message)
            resp.status_code = 401
            return resp

        return f(*args, **kwargs)
    return decorated

#Implement REST Resource
class MyObject(Resource):

    def post(self):
      new_myobject = request.json
      myobject_collection = app.db.myobjects
      result = myobject_collection.insert_one(request.json)

      myobject = myobject_collection.find_one({"_id": ObjectId(result.inserted_id)})

      return myobject

    def get(self, myobject_id):
      myobject_collection = app.db.myobjects
      myobject = myobject_collection.find_one({"_id": ObjectId(myobject_id)})

      if myobject is None:
        response = jsonify(data=[])
        response.status_code = 404
        return response
      else:
        return myobject

class Trip(Resource):

    # Create trip
    @requires_auth
    def post(self):
        new_trip = request.json
        trip_collection = app.db.trips

        result_id = trip_collection.insert_one(new_trip).inserted_id

        trip = trip_collection.find_one({'_id': ObjectId(result_id)})

        return trip

    # Update trip
    def put(self, trip_id):
        new_trip = request.json
        trip_collection = app.db.trips

        trip_collection.update_one({'_id': ObjectId(trip_id)}, {'$set': {'waypoints': new_trip['waypoints']}})

        return trip_collection.find_one({'_id': ObjectId(trip_id)})

    # Delete trip
    def delete(self, trip_id):
        trip_collection = app.db.trips

        delete_result = trip_collection.delete_one({'_id': ObjectId(trip_id)})

        return delete_result.raw_result

    # Get trip by id
    def get(self, trip_id):

        trip_collection = app.db.trips
        trip = trip_collection.find_one({'_id': ObjectId(trip_id)})

        if trip is None:
            response = jsonify(data = [])
            response.status_code = 404
            return response
        else:
            return trip

class User(Resource):

    def post(self):
        new_user = request.json
        user_collection = app.db.users
        #if new_user['user'] is None or new_user['pass'] is None:
            #return({'error': 'Must provide username or password'}, 400, None)

        #if user_collection.find_one({'user': new_user['user']}) is not None:
            #return ({'error': 'Username already taken'}, 400, None)
        #else:
        hashed = bcrypt.hashpw(new_user['pass'].encode('utf-8'), bcrypt.gensalt(12))
        new_user['pass'] = hashed
        user_id = user_collection.insert_one(new_user).inserted_id
        user = user_collection.find_one({'_id': ObjectId(user_id)})
        del user['pass']
        return user
    @requires_auth
    def put(self, name):
        new_trips = request.json
        user_collection = app.db.users

        user_collection.update_one({'name': name}, {'$set' : {'trips': new_trips}})

        return user_collection.find_one({'name': name})
    @requires_auth
    def get(self, name):
        user_collection = app.db.users
        trip_collection = app.db.trips

        user = user_collection.find_one({'name': name})

        if user is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        else:
            trip_ids = user['trips']
            trips = []
            for trip in trip_ids:
                trips.append(trip_collection.find_one({'_id': ObjectId(trip)}))
            return trips

class Verify(Resource):

    def get(self):
        user = request.json
        correct_user = app.db.users.find_one({'user': user['user']})
        if correct_user is None:
            return ({'error': 'User not found.'}, 400, None)

        pass_encoded = user['pass'].encode('utf-8')
        validated = (bcrypt.hashpw(pass_encoded, correct_user['pass']) == correct_user['pass'])

        if validated is True:
            return (None, 200, None)
        else:
            return ({'error': 'Incorrect password.'}, 401, None)

# Add REST resource to API
api.add_resource(MyObject, '/myobject/','/myobject/<string:myobject_id>')
api.add_resource(Trip, '/trips/','/trips/<string:trip_id>')
api.add_resource(User, '/users/','/users/<string:name>')
api.add_resource(Verify, '/verify/')

# provide a custom JSON serializer for flaks_restful
@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(JSONEncoder().encode(data), code)
    resp.headers.extend(headers or {})
    return resp

if __name__ == '__main__':
    # Turn this on in debug mode to get detailled information about request related exceptions: http://flask.pocoo.org/docs/0.10/config/
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    app.run(debug=True)
