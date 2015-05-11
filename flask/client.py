from flask import Flask, url_for, jsonify, request, render_template
from flask.ext.socketio import SocketIO, emit
import requests
import json 

########################
# Flask Initialization #
########################
app = Flask(__name__, static_url_path='')
app.debug = True
socketio = SocketIO(app)

##################
# Flask Settings #
##################
app.config['SECRET_KEY'] = 'secret!'
app.config['DATABASE_WEBHOOK_URL'] = 'http://52.10.249.147:8123/webhook/'
app.config['MY_WEBHOOK_URL'] = 'http://52.24.215.226/webhook/'

######################
# SocketIO Functions #
######################
@socketio.on('car request', namespace='/car')
def test_message(message):
	car_name =  message['data']

	headers = {'Content-Type': 'application/json'}
	payload = {
		'source' : app.config['MY_WEBHOOK_URL'],
		'car_name' : car_name
	}

	r = requests.post(app.config['DATABASE_WEBHOOK_URL'], data=json.dumps(payload), headers=headers)
	print r

	emit('my response', {'data': car_name + ' requested'})

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

#################
# Flask Routing #
#################
@app.route('/', methods=['GET'])
def index():
	return render_template('index.html')

@app.route('/webhook/', methods=['POST'])
def webhook():
	if request.method == 'POST':
		# avail_count['key1'] = request.remote_addr
		print "Received info from " + request.remote_addr
		data = request.get_json()

		print "Data: " + str(data)
		socketio.emit('my response', {'data': data}, namespace='/car')

	return "OK"

if __name__ == '__main__':
	socketio.run(app)
