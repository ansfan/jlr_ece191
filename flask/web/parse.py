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
		
		# if result['results'] == []:
		# 	return False
		# else: 
		# 	self.printDebug('result obj: ' + str(result['results'][0]))
		# 	self.printDebug('objid: ' + result['results'][0]['objectId'])
		# return result['results'][0]

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