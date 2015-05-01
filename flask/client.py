app = Flask(__name__)
app.debug = True

@app.route('/webhook/', methods=['POST'])
def webhook():
	if request.method == 'POST':
		# avail_count['key1'] = request.remote_addr
		print "Received info from " + request.remote_addr
		data = request.form
		print data