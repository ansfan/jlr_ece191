############################
# Begin Parse REST Handler #
############################
import json, httplib, urllib

DEBUG = 1

class parseRESTHandler:
	def __init__(self, App_ID, rest_API_key):
		self.APPLICATION_ID = App_ID
		self.API_KEY = rest_API_key

	# Master debug printout switch
	def printDebug(self, statement):
		if DEBUG:
			print str(statement)

	# Register a user
	def UserRegister(self, first_name, last_name, email, unique_id):
		connection = httplib.HTTPSConnection('api.parse.com', 443)
		connection.connect()
		connection.request('POST', '/1/classes/mainDatabase', json.dumps({
			"first_name" : first_name,
			"last_name" : last_name,
			"email" : email,
			"unique_id" : unique_id,
			"role" : "USER"  # default new user is USER
			 }), {
			"X-Parse-Application-Id": self.APPLICATION_ID,
			"X-Parse-REST-API-Key": self.API_KEY,
			"Content-Type": "application/json"
			 })

		result = json.loads(connection.getresponse().read())
		self.printDebug(result)

		return result['objectId']

	# Login - return false if no account with same unique_id found on parse, else true
	def UserLogin(self, unique_id):
		connection = httplib.HTTPSConnection('api.parse.com', 443)
		params = urllib.urlencode({"where" : json.dumps({
			"unique_id": unique_id,
			 })})
		connection.connect()
		connection.request('GET', '/1/classes/mainDatabase?%s' % params, '', {
			"X-Parse-Application-Id": self.APPLICATION_ID,
			"X-Parse-REST-API-Key": self.API_KEY
			 })

		result = json.loads(connection.getresponse().read())
		self.printDebug('result: ' + str(result))

		try:
			if result['results'] != []:
				self.printDebug('result obj: ' + str(result['results'][0]))
				self.printDebug('objid: ' + result['results'][0]['objectId'])
				return result['results'][0]
		except KeyError:
			self.printDebug('Parse: No account found')
			return False
			
	# Load user
	def UserLoad(self, user_id):
		connection = httplib.HTTPSConnection('api.parse.com', 443)
		connection.connect()
		connection.request('GET', '/1/classes/mainDatabase/' + user_id, '', {
			"X-Parse-Application-Id": self.APPLICATION_ID,
			"X-Parse-REST-API-Key": self.API_KEY
		})
		result = json.loads(connection.getresponse().read())

		self.printDebug('User load result: ' + str(result))

		try:
			if result['objectId'] != []:
				return result
		except KeyError:
			self.printDebug('Failed to load user. Parse responded: ' + result)
			return None

	# Add car
	def AddCar(self, user_id, car_vin, car_name):
		connection = httplib.HTTPSConnection('api.parse.com', 443)
		connection.connect()
		connection.request('POST', '/1/classes/carsDatabase', json.dumps({
			"account" : user_id,
			"car_name" : car_name,
			"car_vin" : car_vin
			 }), {
			"X-Parse-Application-Id": self.APPLICATION_ID,
			"X-Parse-REST-API-Key": self.API_KEY,
			"Content-Type": "application/json"
			 })

		result = json.loads(connection.getresponse().read())
		self.printDebug('Car added: ' + str(result))

		return result['objectId']

	# Delete cars
	def DeleteCar(self, car_obj_id):
		connection = httplib.HTTPSConnection('api.parse.com', 443)
		connection.connect()
		connection.request('DELETE', '/1/classes/carsDatabase/' + car_obj_id, '', {
		       "X-Parse-Application-Id": self.APPLICATION_ID,
		       "X-Parse-REST-API-Key": self.API_KEY
		     })
		result = json.loads(connection.getresponse().read())
		self.printDebug('Car deleted.')

		return True

	# Load all cars owned by dude
	def LoadCars(self, user_id):
		connection = httplib.HTTPSConnection('api.parse.com', 443)
		params = urllib.urlencode({"where" : json.dumps({
			"account": user_id,
			 })})
		connection.connect()
		connection.request('GET', '/1/classes/carsDatabase?%s' % params, '', {
			"X-Parse-Application-Id": self.APPLICATION_ID,
			"X-Parse-REST-API-Key": self.API_KEY
			 })

		result = json.loads(connection.getresponse().read())

		try:
			if result['results'] != []:
				self.printDebug('All cars obj: ' + str(result['results']))
				return result['results']

		except KeyError:
			self.printDebug('Parse: No cars found')
			return False

	# Load all users
	def LoadAllUsers(self):
		connection = httplib.HTTPSConnection('api.parse.com', 443)
		connection.connect()
		connection.request('GET', '/1/classes/mainDatabase', '', {
			"X-Parse-Application-Id": self.APPLICATION_ID,
			"X-Parse-REST-API-Key": self.API_KEY
			 })

		result = json.loads(connection.getresponse().read())

		try:
			if result['results'] != []:
				self.printDebug('All users obj: ' + str(result['results']))
				return result['results']
		except KeyError:
			self.printDebug('Parse: No users found')
			return False

	def LoadCarsWrapper(self, user_id, output):
		output.put(self.LoadCars(user_id))
