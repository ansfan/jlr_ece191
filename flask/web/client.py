from flask import Flask, url_for, jsonify, request, render_template, flash, redirect, session, g
from flask.ext.socketio import SocketIO, emit
import requests
import json 
import settings_client as settings

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
app.config['DATABASE_WEBHOOK_URL'] = settings.RVI_DATABASE_WEBHOOK_URL
app.config['FLASK_WEBHOOK_URL'] = settings.RVI_FLASK_WEBHOOK_URL

######################
# SocketIO Functions #
######################
@socketio.on('car request')
def test_message(message):
	print message
	car_name =  message['data']

	headers = {'Content-Type': 'application/json'}
	payload = {
		'source' : app.config['FLASK_WEBHOOK_URL'],
		'car_name' : car_name
	}

	r = requests.post(app.config['DATABASE_WEBHOOK_URL'], data=json.dumps(payload), headers=headers)
	# print r

	emit('my response', {'data': car_name + ' requested'}, namespace='/car')

# @socketio.on('my broadcast event', namespace='/test')
# def test_message2(message):
# 	print message['data']
# 	emit('my response', {'data': message['data']}, broadcast=True)

@socketio.on('connect', namespace='/car')
def test_connect():
	emit('my response', {'data': 'Connected'})

@socketio.on('disconnect', namespace='/car')
def test_disconnect():
	print 'Client disconnected'

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
	return render_template('templogin.html')

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_vehicle():
	if request.method == 'POST':
		car_name = request.form['car_name']
		car_vin = request.form['car_vin']

		r = parse.AddCar(g.user.id, car_vin, car_name)

		if r:
			flash('Your car ' + car_name + ' is added!')

		return redirect(url_for('index'))

	return render_template('add.html')

@app.route('/authhandler/loginGoogle')
def google_login():
	next_url = request.args.get('next') or url_for('index')
	return google.authorize(callback=url_for('google_authorized',
		next=next_url,
		_external=True))

@app.route('/index', methods=['GET'])
@login_required
def index():
	user = g.user

	list_of_cars = parse.LoadCars(user.id)
	if not list_of_cars:
		list_of_cars = []

	return render_template('index.html',
		user = user,
		cars_list = list_of_cars)

@app.route('/car/<vin>', methods=['GET'])
@login_required
def index_vehicle(vin):
	user = g.user

	list_of_cars = parse.LoadCars(user.id)

	return render_template('index.html',
		user = user,
		cars_list = list_of_cars,
		car_namespace = vin)

@app.route('/webhook/', methods=['POST'])
def webhook():
	if request.method == 'POST':
		# avail_count['key1'] = request.remote_addr
		print "Received info from " + request.remote_addr
		data = request.get_json()

		vin = '/' + data['vin']

		print "Data: " + str(data)
		socketio.emit('my response', {'data': data}, namespace=vin)

	return "OK"

@app.route('/dashboard', methods=['GET'])
def dashboard():
	return render_template('dashboard.html')
	
@app.route('/logout', methods=['GET'])
@login_required
def logout():
	logout_user()
	return redirect(url_for('login'))

if __name__ == '__main__':
	socketio.run(app)
