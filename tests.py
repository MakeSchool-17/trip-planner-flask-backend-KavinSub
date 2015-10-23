import server
import unittest
import json
import base64
from pymongo import MongoClient

class FlaskrTestCase(unittest.TestCase):

    def default_auth_header(self):
        return self.generate_auth_header('user', 'pass')

    def generate_auth_header(self, username, password):
        authString = username + ":" + password
        return {'Authorization': 'Basic ' + base64.b64encode(authString.encode('utf-8')).decode('utf-8')}

    def setUp(self):
      self.app = server.app.test_client()
      # Run app in testing mode to retrieve exceptions and stack traces
      server.app.config['TESTING'] = True

      # Inject test database into application
      mongo = MongoClient('localhost', 27017)
      db = mongo.test_database
      server.app.db = db

      # Drop collection (significantly faster than dropping entire db)
      db.drop_collection('myobjects')

    # MyObject tests

    def test_posting_myobject(self):
      response = self.app.post('/myobject/',
        data=json.dumps(dict(
          name="A object"
        )),
        content_type = 'application/json')

      responseJSON = json.loads(response.data.decode())

      self.assertEqual(response.status_code, 200)
      assert 'application/json' in response.content_type
      assert 'A object' in responseJSON["name"]


    def test_getting_object(self):
      response = self.app.post('/myobject/',
        data=json.dumps(dict(
          name="Another object"
        )),
        content_type = 'application/json')

      postResponseJSON = json.loads(response.data.decode())
      postedObjectID = postResponseJSON["_id"]

      response = self.app.get('/myobject/'+postedObjectID)
      responseJSON = json.loads(response.data.decode())

      self.assertEqual(response.status_code, 200)
      assert 'Another object' in responseJSON["name"]

    def test_getting_non_existent_object(self):
      response = self.app.get('/myobject/55f0cbb4236f44b7f0e3cb23')
      self.assertEqual(response.status_code, 404)

    # def test_creating_trip(self):
    #     trip = {'user':'Kav', 'waypoints':[('Golden Gate Bridge', 23.57, 40.1),('Eiffel Tower', 13.1, 90.8)]}
    #     response = self.app.post('/trips/', data = json.dumps(trip), content_type = 'application/json')
    #     responseJSON = json.loads(response.data.decode())
    #     self.assertEqual(response.status_code, 200)
    #     assert 'Kav' in responseJSON['user']
    #
    # def test_updating_trip(self):
    #     trip = {'user':'Kav', 'waypoints':[('Golden Gate Bridge', 23.57, 40.1)]}
    #     response = self.app.post('/trips/', data = json.dumps(trip), content_type = 'application/json')
    #     responseJSON = json.loads(response.data.decode())
    #
    #     responseJSON['waypoints'].append(('Eiffel Tower', 13.1, 90.8))
    #     new_response = self.app.put('/trips/'+ responseJSON['_id'], data = json.dumps(responseJSON), content_type = 'application/json')
    #     new_responseJSON = json.loads(new_response.data.decode())
    #
    #     self.assertEqual(new_response.status_code, 200)
    #     assert new_responseJSON['_id'] == responseJSON['_id']
    #     assert 'Kav' in responseJSON['user']
    #
    # def test_deleting_trip(self):
    #     trip = {'user':'Kav', 'waypoints':[('Golden Gate Bridge', 23.57, 40.1)]}
    #     response = self.app.post('/trips/', data = json.dumps(trip), content_type = 'application/json')
    #     trip_id = json.loads(response.data.decode())['_id']
    #
    #     new_response = self.app.delete('/trips/' + trip_id)
    #     new_responseJSON = json.loads(new_response.data.decode())
    #
    #     self.assertEqual(new_response.status_code, 200)
    #
    # def test_getting_trip(self):
    #     trip = {'user':'Kav', 'waypoints':[('Golden Gate Bridge', 23.57, 40.1)]}
    #
    #     response = self.app.post('/trips/', data = json.dumps(trip), content_type = 'application/json')
    #     responseJSON = json.loads(response.data.decode())
    #     trip_id = responseJSON['_id']
    #
    #     new_response = self.app.get('/trips/' + trip_id)
    #     new_responseJSON = json.loads(new_response.data.decode())
    #
    #     self.assertEqual(new_response.status_code, 200)
    #     assert 'Kav' in responseJSON['user']
    #
    # # Test created prior to implementation of authentication
    # def test_creating_user(self):
    #     user = {'name': 'Kav', 'pass': '1@!!!', 'trips':[]}
    #
    #     response = self.app.post('/users/', data = json.dumps(user), content_type = 'application/json')
    #     responseJSON = json.loads(response.data.decode())
    #
    #     self.assertEqual(response.status_code, 200)
    #     assert 'Kav' in responseJSON['name']
    #
    # def test_updating_user(self):
    #     user = {'name': 'Kav', 'pass': '1@!!!', 'trips':[]}
    #     trip = {'user':'Kav', 'waypoints':[('Golden Gate Bridge', 23.57, 40.1)]}
    #
    #     # Create user
    #     user_response = self.app.post('/users/', data = json.dumps(user), content_type = 'application/json')
    #     user_responseJSON = json.loads(user_response.data.decode())
    #
    #     # Create trip
    #     trip_response = self.app.post('/trips/', data = json.dumps(trip), content_type = 'application/json')
    #     trip_responseJSON = json.loads(trip_response.data.decode())
    #
    #     # Update user
    #     user['trips'].append(trip_responseJSON['_id'])
    #     new_response = self.app.put('/users/' + user['name'], data = json.dumps(user['trips']), content_type = 'application/json')
    #     new_responseJSON = json.loads(new_response.data.decode())
    #
    #     # Check
    #     self.assertEqual(new_response.status_code, 200)
    #     assert 'Kav' in new_responseJSON['name']
    #     assert trip_responseJSON['_id'] == new_responseJSON['trips'][0]
    #
    # def test_getting_usertrips(self):
    #     user = {'name': 'Kav', 'pass': '1@!!!', 'trips':[]}
    #     trip = {'name': 'SF trip', 'waypoints':[('Golden Gate Bridge', 23.57, 40.1)]}
    #
    #     trip_response = self.app.post('/trips/', data = json.dumps(trip), content_type = 'application/json')
    #     trip_responseJSON = json.loads(trip_response.data.decode())
    #
    #     user['trips'].append(trip_responseJSON['_id'])
    #     self.app.post('/users/', data = json.dumps(user), content_type = 'application/json')
    #
    #     get_response = self.app.get('/users/' + user['name'])
    #     trips = json.loads(get_response.data.decode())
    #
    #     self.assertEqual(get_response.status_code, 200)

    def test_registration(self):
        user = {'user': 'Kav', 'pass': '1@!!!', 'trips': []}

        register_response = self.app.post('/users/', data = json.dumps(user), content_type = 'application/json')
        register_responseJSON = json.loads(register_response.data.decode())
        self.assertEqual(register_response.status_code, 200)
        assert 'Kav' in register_responseJSON['user']

    def test_authorization(self):
        user = {'user': 'Kav', 'pass': '1@!!!', 'trips': []}
        # First create user
        self.app.post('/users/', data = json.dumps(user), content_type = 'application/json')
        # Test correct password
        authorize_response = self.app.get('/verify/', data = json.dumps(user), content_type = 'application/json')
        # Change password to wrong one
        user['pass'] = '2@!!!'
        false_response = self.app.get('/verify/', data = json.dumps(user), content_type = 'application/json')

        self.assertEqual(authorize_response.status_code, 200)
        self.assertEqual(false_response.status_code, 401)

    def test_authorized_tripcreate(self):
        user = {'user': 'Kav', 'pass': '1@!!!', 'trips': []}
        trip = {'name': 'SF trip', 'waypoints':[('Golden Gate Bridge', 23.57, 40.1)]}
        trip_2 = {'name': 'France trip', 'waypoints':[('Eiffel Tower', 0, 1)]}

        # First create user
        self.app.post('/users/', data = json.dumps(user), content_type = 'application/json')
        # Now create trip given correct user data

        #header = {"Authorization": }
        valid_post = self.app.post('/trips/', headers=self.generate_auth_header(user['user'], user['pass']),  data=json.dumps(trip), content_type = 'application/json')

        # Change password to wrong one
        user['pass'] = '2@!!!'
        # Now create trip given incorrect user data
        invalid_post = self.app.post('/trips/', headers=self.generate_auth_header(user['user'], user['pass']), data = json.dumps(trip), content_type = 'application/json')

        self.assertEqual(valid_post.status_code, 200)
        self.assertEqual(invalid_post.status_code, 401)

    def test_authorized_tripget(self):
        user = {'user': 'Kav', 'pass': '1@!!!', 'trips': []}
        trip = {'name': 'SF trip', 'waypoints':[('Golden Gate Bridge', 23.57, 40.1)]}

        # First create user and trip
        self.app.post('/users/', data = json.dumps(user), content_type = 'application/json')
        trip_JSON = json.loads(self.app.post('/trips/', headers = self.generate_auth_header(user['user'], user['pass']), data=json.dumps(trip), content_type='application/json').data.decode())
        # Associate trip with user
        user['trips'].append(trip_JSON['_id'])
        put_response = self.app.put('/users/' + user['user'], headers = self.generate_auth_header(user['user'], user['pass']), data = json.dumps(user['trips']), content_type = 'application/json')
        # Now get all associated trips
        get_response = self.app.get('/users/' + user['user'], headers = self.generate_auth_header(user['user'], user['pass']))
        tripsJSON = json.loads(get_response.data.decode())

        self.assertEqual(put_response.status_code, 200)
        self.assertEqual(put_response.status_code, 200)
        #print(tripsJSON)
        
if __name__ == '__main__':
    unittest.main()
