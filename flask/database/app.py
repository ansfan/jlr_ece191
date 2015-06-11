from flask import Flask, url_for, jsonify, request
import time
import requests
import json
import settings_app as settings

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

########################
# Flask Initialization #
########################
app = Flask(__name__)
app.debug = True

##################
# Flask Settings #
##################
app.config['SECRET_KEY'] = settings.SECRET_KEY

################
# RVI Settings #
################
from rviwebconsumer import RVIConsumer
rvi_thread_pool = {}

import hbasepull
hbasetable = hbasepull.RVIHBaseTable()

def maxDateWrapper(vin, output):
	output.put([vin, hbasetable.max_date(vin)])

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
		response_address = data['source']
		response_attr = data['car_name']

		if response_attr:
			response = response_attr.split(' ')

			try:
				if (response[1] == 'end'):
					try:
						rvi_thread_pool[response[0]].shutdown()
					except KeyError:
						print "Unable to find thread for car: " + response[0]

			except IndexError:
				if response[0] in rvi_thread_pool:
					print "Thread for " + response[0] + " is already running. "

					if not rvi_thread_pool[response[0]].is_running():
						print "Thread " + response[0] + " has stopped; restarting thread."
						rvi_thread = RVIConsumer(settings.RVI_KAFKA_ENDPOINT, settings.RVI_KAFKA_TOPIC, response[0], settings.FLASK_WEBHOOK_URL)
						rvi_thread.start()
						rvi_thread_pool[response[0]] = rvi_thread

					# need to optimize for multi web server support
				else:
					print "Sending data to: " + response_address
					print "With data type: " + response[0]

					vin1 = RVIConsumer(settings.RVI_KAFKA_ENDPOINT, settings.RVI_KAFKA_TOPIC, response[0], settings.FLASK_WEBHOOK_URL)
					vin1.start()

					rvi_thread_pool[response[0]] = vin1

	return "OK\n"

@app.route('/history/', methods=['POST'])
def history():
	if request.method == 'POST':
		print "Received data from " + request.remote_addr

		data = request.get_json()

		# implement error catcher http://flask.pocoo.org/docs/0.10/patterns/apierrors/
		print 'Start time: ' + str(data['start'])
		print 'End time: ' + str(data['end'])
		start_date = str(data['start'])
		end_date = str(data['end'])
		car_name = data['car']
		fat_array = hbasetable.query_by_date(car_name, start_date, end_date)
		return str(fat_array)

@app.route('/lastpacket/', methods=['POST'])
def latest():
	if request.method == 'POST':
		print "Received request from " + request.remote_addr

		data = request.get_json()

		print 'List of Vins data: ' + str(data)
		list_of_vins = data['car_vins']
	
		for vin in list_of_vins:
			print vin
	
		result = []
		for vin in list_of_vins:
			vin = str(vin)
			result.append([vin, hbasetable.max_date(vin)])
		
		return_payload = {
			'result': result
		}
		return str(return_payload)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8123)
