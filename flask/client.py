from flask import Flask, url_for, jsonify, request, render_template
from flask.ext.socketio import SocketIO, emit

########################
# Flask Initialization #
########################
app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'secret!'
app.debug = True
socketio = SocketIO(app)

######################
# SocketIO Functions #
######################
@socketio.on('my event', namespace='/test')
def test_message(message):
	print message['data']
	emit('my response', {'data': message['data']})

@socketio.on('my broadcast event', namespace='/test')
def test_message2(message):
	print message['data']
	emit('my response', {'data': message['data']}, broadcast=True)

@socketio.on('connect', namespace='/test')
def test_connect():
	emit('my response', {'data': 'Connected'})

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
	print('Client disconnected')

###################
# Flask Functions #
###################
@app.route('/')
def index():
	return render_template('index.html')

@app.route('/webhook/', methods=['POST'])
def webhook():
	if request.method == 'POST':
		# avail_count['key1'] = request.remote_addr
		print "Received info from " + request.remote_addr
		data = request.get_json()

		print "Data: " + str(data)
		socketio.emit('my response', {'data': data}, namespace='/test')

	return "OK"

if __name__ == '__main__':
	socketio.run(app)