from flask import Flask, url_for, jsonify, request, render_template, flash, redirect, session, g
from flask.ext.socketio import SocketIO, emit
import requests
import json 
import settings_client as settings
import threading, Queue
import logging
import ast
import time
from datetime import datetime
logging.basicConfig()

#################
# Parse Configs #
#################
from parse import parseRESTHandler

parse = parseRESTHandler(settings.PARSE_APPLICATION_ID, settings.PARSE_REST_API_KEY)

########################
# Flask Initialization #
########################
app = Flask(__name__, static_url_path='')
app.debug = True
socketio = SocketIO(app)

#############################
# Importing database models #
#############################
import models

####################
# Global Functions #
####################
def pretty_date(time):
	now = datetime.now()
	diff = now - datetime.fromtimestamp(time)
	second_diff = diff.seconds
	day_diff = diff.days

	if day_diff < 0:
		return ''

	elif day_diff == 0:
		if second_diff < 10:
			return "Just now"
		if second_diff < 60:
			return str(second_diff) + " seconds ago"
		if second_diff < 120:
			return "A minute ago"
		if second_diff < 3600:
			return str(second_diff / 60) + " minutes ago"
		if second_diff < 7200:
			return "An hour ago"
		if second_diff < 86400:
			return str(second_diff / 3600) + " hours ago"
	if day_diff == 1:
		return "Yesterday"
	if day_diff < 7:
		return str(day_diff) + " days ago"
	if day_diff < 31:
		return str(day_diff / 7) + " weeks ago"
	if day_diff < 365:
		return str(day_diff / 30) + " months ago"
	return str(day_diff / 365) + " years ago"

def yyyymmddToEpoch(wordDate):
	return int(time.mktime(time.strptime(wordDate, "%Y-%m-%d %I:%M%p")))

def decode_dict(item):
	result = {}
	for k,v in item.items():
		k = str(k)
		if isinstance(v, dict):
			v = decode_dict(v)
		else:
			v = str(v)

		result[k] = v

	return result

def massageUnicode(list_of_data):
	new_datablocks = list_of_data

	for data_block in new_datablocks:
		temp_data = []	
		for item in eval(data_block['data']):
			item = decode_dict(item)
			temp_data.append(item)

		data_block['data'] = temp_data

	return new_datablocks

################
# Google OAuth #
################
from flask_oauth import OAuth

oauth_google = OAuth()
google = oauth_google.remote_app('google',
	base_url='https://www.google.com/accounts/',
	authorize_url='https://accounts.google.com/o/oauth2/auth',
	request_token_url=None,
	request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile', 'response_type': 'code'},
	access_token_url='https://accounts.google.com/o/oauth2/token',
	access_token_method='POST',
	access_token_params={'grant_type': 'authorization_code'},
	consumer_key=settings.GOOGLE_CLIENT_ID,
	consumer_secret=settings.GOOGLE_CLIENT_SECRET)

@app.route('/oauth2callback')
@google.authorized_handler
def google_authorized(resp):
	next_url = request.args.get('next') or url_for('index')
	if resp is None:
		flash(u"You're denied the request to sign in from Google.")
		return url_for('index')

	# Google authorized
	print 'google authorized: ' + str(resp)

	access_token = resp['access_token']
	session['oauth_token'] = (access_token, '')

	# use obtained google token to get profile info
	if access_token:
		print access_token
		r = requests.get('https://www.googleapis.com/oauth2/v3/userinfo?access_token=' + access_token)

		if r.ok:
			data = json.loads(r.text)
			print 'Response from Google: ' + str(data)

			google_id = 'g_' + data['sub']
			google_last_name = data['family_name']
			google_first_name = data['given_name']
			google_email = data['email']
			google_email_verified = data['email_verified']

			parse_user = parse.UserLogin(google_id)

			if parse_user:
				# Retrieve user info from parse
				parse_parse_id = parse_user['objectId']
				parse_unique_id = parse_user['unique_id']
				parse_email = parse_user['email']
				parse_first_name = parse_user['first_name']
				parse_last_name = parse_user['last_name']

				local_user = models.User(parse_parse_id, parse_unique_id, parse_email, parse_first_name, parse_last_name)
				
				login_user(local_user)

			else:
				print 'No user found'
				new_parse_id = parse.UserRegister(google_first_name, google_last_name, google_email, google_id)
				
				parse_user = parse.UserLoad(new_parse_id)
				
				# Retrieve user info from parse
				parse_parse_id = parse_user['objectId']
				parse_unique_id = parse_user['unique_id']
				parse_email = parse_user['email']
				parse_first_name = parse_user['first_name']
				parse_last_name = parse_user['last_name']
				parse_role = parse_user['role']

				local_user = models.User(parse_parse_id, parse_unique_id, parse_email, parse_first_name, parse_last_name)
				login_user(local_user)

				return redirect(url_for('add_vehicle'))
				
		else:
			print "Google Error"
			flash("Google Login Error")

	return redirect(url_for('index'))

###############
# Flask Login #
###############
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

login_manager = LoginManager()
login_manager.init_app(app)

# Tell Flask-Login where the login page is
login_manager.login_view = "login"
# The message to flash to un-authenticated users
login_manager.login_message = "You need to log in to view this page"
login_manager.refresh_view = "index"

@login_manager.user_loader
def load_user(userid):
	print 'Attempting to load user ' + str(userid)

	user = parse.UserLoad(userid)
	if user:
		parse_id = user['objectId']
		unique_id = user['unique_id']
		email = user['email']
		first_name = user['first_name']
		last_name = user['last_name']
		role = user['role']

		print 'User ' + first_name + ' loaded'
		
		local_user = models.User(parse_id, unique_id, email, first_name, last_name, role_assigned=role)
		return local_user

##################
# Flask Settings #
##################
app.config['SECRET_KEY'] = settings.SECRET_KEY
app.config['DATABASE_HISTORY_URL'] = settings.RVI_DATABASE_URL + 'history/'
app.config['DATABASE_WEBHOOK_URL'] = settings.RVI_DATABASE_URL + 'webhook/'
app.config['DATABASE_LASTPACKET_URL'] = settings.RVI_DATABASE_URL + 'lastpacket/'
app.config['FLASK_WEBHOOK_URL'] = settings.RVI_FLASK_WEBHOOK_URL

######################
# SocketIO Functions #
######################
@socketio.on('car request')
def test_message(message):
	print 'car request: ' + message
	car_name =  message['data']

	headers = {'Content-Type': 'application/json'}
	payload = {
		'source' : app.config['FLASK_WEBHOOK_URL'],
		'car_name' : car_name
	}

	r = requests.post(app.config['DATABASE_WEBHOOK_URL'], data=json.dumps(payload), headers=headers)
	# print r

	prep_carname = '/' + car_name
	
	emit('my response', {'data': car_name + ' requested'}, namespace=prep_carname)

def create_namespace(name):
	print "Create namespace called"
	namespace = '/' + name
	@socketio.on('connect', namespace=namespace)
	def new_tunnel():
		print "Tunnel created"
		emit('my response', {'data': 'Connected'})

@socketio.on('connect', namespace='/car')
def test_connect():
	emit('my response', {'data': 'Connected'})

@socketio.on('disconnect', namespace='/car')
def test_disconnect():
	print 'Client disconnected'

@socketio.on_error_default
def default_error_handler(e):
	print e.message, e.args

##############################
# Start website redirections #
##############################
@app.before_request
def before_request():
	g.user = current_user

@app.errorhandler(404)
def error_notfound(error):
	return 'This page cannot be found! Error caught.'

@app.errorhandler(500)
def error_internalserver(error):
	return 'Internal server error caught.'

#################
# Flask Routing #
#################
@app.route('/', methods=['GET'])
def login():
	return render_template('login.html')

@app.route('/add', methods=['POST'])
@app.route('/add/', methods=['POST'])
@login_required
def add_vehicle():
	if request.method == 'POST':
		car_name = request.form['car_name']
		car_vin = request.form['car_vin']

		r = parse.AddCar(g.user.id, car_vin, car_name)

		if r:
			flash('Your car ' + car_name + ' is added!')

		return redirect(url_for('index'))

@app.route('/authhandler/loginGoogle')
def google_login():
	next_url = request.args.get('next') or url_for('index')
	return google.authorize(callback=url_for('google_authorized',
		next=next_url,
		_external=True))

@app.route('/index', methods=['GET'])
@app.route('/index/', methods=['GET'])
@login_required
def index():
	user = g.user

	list_of_cars = parse.LoadCars(user.id)

	list_of_vin = []
	if list_of_cars:
		for car in list_of_cars:
			list_of_vin.append(car['car_vin'])

		headers = {'Content-Type': 'application/json'}
		payload = {
			'car_vins' : list_of_vin
		}
		try:
			print "Sending last known request to DB."
			r = requests.post(app.config['DATABASE_LASTPACKET_URL'], data=json.dumps(payload), headers=headers)

			print r.text

			list_of_timestamps = ast.literal_eval(r.text)
			
			print list_of_timestamps
			list_of_timestamps = list_of_timestamps['result']			

			for car in list_of_cars:
				for entry in list_of_timestamps:
					if (car['car_vin'] == entry[0]):
						if (entry[1] is not '0'):
							car['last_entry'] = pretty_date(int(entry[1]))
						else:
							car['last_entry'] = 'No Data'

			print 'EVERYTHING: ' + str(list_of_cars)

		except Exception as e:
			print "Error establishing connection to DB."
			print e.message, e.args
			flash("Error establishing connection to DB.")

	else: 
		list_of_vin = None

	return render_template('index.html',
		user = user,
		cars_list = list_of_cars)

@app.route('/car/<vin>', methods=['GET'])
@app.route('/car/<vin>/', methods=['GET'])
@login_required
def index_vehicle(vin):
	user = g.user

	list_of_cars = parse.LoadCars(user.id)

	headers = {'Content-Type': 'application/json'}
	payload = {
		'source' : app.config['FLASK_WEBHOOK_URL'],
		'car_name' : vin
	}

	try:
		print "Sending data request to DB."
		r = requests.post(app.config['DATABASE_WEBHOOK_URL'], data=json.dumps(payload), headers=headers)

		create_namespace(vin)
		
	except Exception as e:
		print "Error establishing connection to DB."
		print e.message, e.args
		flash("Error establishing connection to DB.")

	return render_template('dashboard.html',
		user = user,
		cars_list = list_of_cars,
		car_namespace = vin)

@app.route('/webhook', methods=['POST'])
@app.route('/webhook/', methods=['POST'])
def webhook():
	if request.method == 'POST':
		print "Received info from " + request.remote_addr
		data = request.get_json()
		
		parsed_data = json.loads(data)
		vin = '/' + str(parsed_data['vin'])

		print "Data: " + str(data)
		print "Vin: " + str(vin)

		socketio.emit('my response', {'data': data}, namespace=vin)

	return "OK"

@app.route('/history', methods=['GET', 'POST'])
@app.route('/history/', methods=['GET', 'POST'])
def history():
	user = g.user

	data = None
	vin = None
	
	list_of_cars = parse.LoadCars(user.id)

	deunicoded_data = None

	if request.method == 'POST':
		start_date = request.form['start_date']
		start_time = request.form['start_time']
		end_date = request.form['end_date']
		end_time = request.form['end_time']
		car_selected = request.form['car']

		print start_date
		print start_time
		print end_date
		print end_time

		headers = {'Content-Type': 'application/json'}
		payload = {
			'start' : yyyymmddToEpoch(start_date + ' ' + start_time),
			'end' : yyyymmddToEpoch(end_date + ' ' + end_time),
			'car' : car_selected
		}

		try:
			print "Requesting historical data from " + start_date + " to " + end_date + " for vehicle " + car_selected
			r = requests.post(app.config['DATABASE_HISTORY_URL'], data=json.dumps(payload), headers=headers)

			print r.json()
			data_payload = r.json()
			data = data_payload['payload']

			print data

			deunicoded_data = massageUnicode(data)

			print deunicoded_data
	
		except Exception as e:
			print "Error establishing connection to DB."
			print e.message, e.args
			flash("Error establishing connection to DB.")

	return render_template('history.html', 
		data=deunicoded_data,
		car=vin,
		user=user,
		cars_list=list_of_cars)

@app.route('/dashboard', methods=['GET'])
def dashboard():

	user = g.user

	list_of_cars = parse.LoadCars(user.id)
	
	return render_template('dashboard.html',
		user = user,
		cars_list = list_of_cars)
	
@app.route('/delete/<obj>', methods=['GET'])
@app.route('/delete/<obj>/', methods=['GET'])
@login_required
def delete_car(obj):
	delete_result = parse.DeleteCar(obj)

	flash('Your car is deleted.')

	return redirect(url_for('index'))

@app.route('/admin', methods=['GET', 'POST'])
@app.route('/admin/', methods=['GET', 'POST'])
@login_required
def admin_panel():
	user = g.user

	if user.is_admin():
		print str(user) + ' is admin'

		list_of_cars = parse.LoadCars(user.id)
		all_users = parse.LoadAllUsers()
		list_of_ids = []
		for users in all_users:
			print 'this is users' + str(users)
			list_of_ids.append(users['objectId'])

		q = Queue.Queue()
		threads = [threading.Thread(target=parse.LoadCarsWrapper, args=(user_id,q)) for user_id in list_of_ids]

		for thread in threads:
			thread.start()

		for thread in threads:
			thread.join()

		for i in range(len(all_users)):
			data = q.get()
			print data
			for users in all_users:
				if (data != None and users['objectId'] == data[0]['account']):
					users['cars_list'] = data

		return render_template('admin.html',
			user=user,
			cars_list=list_of_cars,
			users_list=all_users)

	else:
		flash('That page is for admin only.')

		return redirect(url_for('index'))

@app.route('/logout', methods=['GET'])
@login_required
def logout():
	logout_user()
	return redirect(url_for('login'))

if __name__ == '__main__':
	socketio.run(app)
