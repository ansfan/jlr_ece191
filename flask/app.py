from flask import Flask, url_for, jsonify, request
import time
import requests
from celery import Celery

app = Flask(__name__)
app.debug = True
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

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
with open('../cabspottingdata/new_abboip.txt') as inputfile:
	for line in inputfile:
		testdata.append(jsonifyCSData(line))

# Celery tasks
@celery.task(bind=True)
def send_cab_data(self, dest, name):
	with app.app_context():
		for items in testdata:
			payload = {
				'data' : items,
				'car_name' : name
			}
			r = requests.post(dest, params=payload)
			time.sleep(100)
	return True

@app.route('/')
def api_root():
	return 'Welcome'

@app.route('/webhook/', methods=['POST'])
def webhook():
	if request.method == 'POST':
		# avail_count['key1'] = request.remote_addr
		print "Received connection from " + request.remote_addr
		data = request.form

		# implement error catcher http://flask.pocoo.org/docs/0.10/patterns/apierrors/

		response_address = data['source']
		response_attr = data['car_name']
		
		task = send_cab_data.delay(response_address, response_attr)
		if task:
			print "Sent complete."
	return "OK\n"

@app.route('/avail')
def avail():
	return jsonify(avail_count)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080)
