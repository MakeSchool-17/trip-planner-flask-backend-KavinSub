from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
from pymongo import MongoClient
from bson.objectid import ObjectId
from utils.mongo_json_encoder import JSONEncoder

# Basic Setup
app = Flask(__name__)
mongo = MongoClient('localhost', 27017)
app.db = mongo.develop_database
api = Api(app)

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

        user_id = user_collection.insert_one(new_user).inserted_id
        user = user_collection.find_one({'_id': ObjectId(user_id)})

        return user

    def put(self, name):
        new_trips = request.json
        user_collection = app.db.users

        user_collection.update_one({'name': name}, {'$set' : {'trips': new_trips}})

        return user_collection.find_one({'name': name})

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




# Add REST resource to API
api.add_resource(MyObject, '/myobject/','/myobject/<string:myobject_id>')
api.add_resource(Trip, '/trips/','/trips/<string:trip_id>')
api.add_resource(User, '/users/','/users/<string:name>')

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
