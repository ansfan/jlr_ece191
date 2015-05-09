from flask import Flask, url_for, jsonify, request
import time
import requests
from celery import Celery
import json

##########################
# Self-Defined Functions #
##########################
def jsonifyCSData(data):
	data_splitted = data.split(" ")
	result = {
		'lat' : data_splitted[0],
		'long' : data_splitted[1],
		'occ' : data_splitted[2],
		'time' : str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(data_splitted[3]))))
	}
	return result

# Import data
testdata = []
with open('../cabspottingdata/new_abboip2.txt') as inputfile:
	for line in inputfile:
		testdata.append(jsonifyCSData(line))

########################
# Flask Initialization #
########################
app = Flask(__name__)
app.debug = True

############
# Settings #
############
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

####################
# Celery Functions #
####################
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@celery.task(bind=True)
def send_cab_data(self, dest, payload):
	with app.app_context():
		headers = {'Content-Type': 'application/json'}
		r = requests.post(dest, data=json.dumps(payload), headers=headers)
	return True

#################
# Flask Routing #
#################
@app.route('/')
def index():
	return 'Welcome'

@app.route('/webhook/', methods=['POST'])
def webhook():
	if request.method == 'POST':
		# avail_count['key1'] = request.remote_addr
		print "Received connection from " + request.remote_addr
		
		data = request.get_json()

		# implement error catcher http://flask.pocoo.org/docs/0.10/patterns/apierrors/
		# print data['source']
		# print data['car_name']
		response_address = data['source']
		response_attr = data['car_name']

		print "Sending data to: " + response_address
		print "With data type: " + response_attr

		for items in testdata:
			payload = {
				'data' : items,
				'car_name' : response_attr
			}
			task = send_cab_data.apply_async(args=[response_address, payload])

		if task:
			print "Sent complete."

	return "OK\n"

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080)
