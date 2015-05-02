from flask import Flask, url_for, jsonify, request

app = Flask(__name__)
app.debug = True

@app.route('/webhook/', methods=['POST'])
def webhook():
	if request.method == 'POST':
		# avail_count['key1'] = request.remote_addr
		print "Received info from " + request.remote_addr
		data = request.get_json()

		print "Data: " + str(data)

	return "OK"

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8081)