import os
BASEDIR = os.path.abspath(os.path.dirname(__file__))
from datetime import datetime

##########################
# Initializing Flask app #
##########################
from flask import Flask, render_template, request, flash, redirect, session, url_for, g
from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__, static_folder='static', static_url_path='')
app.config['DEBUG'] = True
app.config['CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = 'you-will-never-guess'

app.swgi_app = ProxyFix(app.wsgi_app)

##################
# Error Handlers #
##################
@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for('index')), 404

##############################
# Start website redirections #
##############################
@app.route('/')
def index():
	return render_template('index.html')

@app.route('/timeline')
def timetine():
	return render_template('timeline.html')

@app.route('/staten')
def trans_staten():
	return render_template('/transportation/staten.html')

@app.route('/subway')
def trans_subway():
	return render_template('/transportation/subway.html')

@app.route('/ferry')
def trans_ferry():
	return render_template('/transportation/ferry.html')

@app.route('/publicon')
def trans_publicon():
	return render_template('/transportation/publicon.html')

@app.route('/publicabove')
def trans_publicabove():
	return render_template('/transportation/publicabove.html')

@app.route('/commissioners')
def urban_commissioners():
	return render_template('/urban/commissioners.html')

@app.route('/brooklyn')
def urban_brooklyn():
	return render_template('/urban/brooklyn.html')

@app.route('/mosesjacobs')
def urban_mosesjacobs():
	return render_template('/urban/mosesjacobs.html')

@app.route('/freshkillspark')
def urban_freshkillspark():
	return render_template('/urban/freshkillspark.html')

@app.route('/trash')
def san_trash():
	return render_template('/sanitation/trash.html')

@app.route('/freshkillslandfill')
def san_freshkillslandfill():
	return render_template('/sanitation/freshkillslandfill.html')

@app.route('/sanitationtoday')
def san_today():
	return render_template('/sanitation/today.html')

@app.route('/mapping')
def data_mapping():
	return render_template('/data/mapping.html')

@app.route('/innovation')
def data_innovation():
	return render_template('/data/innovation.html')

@app.route('/greatmistake')
def muni_brooklyn():
	return render_template('/muni/brooklyn.html')

@app.route('/chinatown')
def muni_chinatown():
	return render_template('/muni/chinatown.html')

@app.route('/wtc')
def project_wtc():
	return render_template('/projects/wtc.html')

@app.route('/un')
def project_un():
	return render_template('/projects/un.html')

@app.route('/zoningpion')
def zoninghousing_zoningpion():
	return render_template('/zoninghousing/zoningpion.html')

@app.route('/lower')
def zoninghousing_lower():
	return render_template('/zoninghousing/lower.html')

@app.route('/housingact')
def zoninghousing_housingact():
	return render_template('/zoninghousing/housingact.html')

@app.route('/zoningreso')
def zoninghousing_zoningreso():
	return render_template('/zoninghousing/zoningreso.html')

@app.route('/plannyc')
def future_plannyc():
	return render_template('/future/plannyc.html')

@app.route('/borough')
def future_borough():
	return render_template('/future/borough.html')

@app.route('/plan')
def future_plan():
	return render_template('/future/plan.html')

@app.route('/abib')
def abib():
	return render_template('abib.html')

@app.route('/images')
def images():
	return render_template('images.html')

# asdfsadf
# @app.route('/greenyc')
# def future_greenyc():
# 	return render_template('/future/greenyc.html')

@app.route('/onecity')
def future_onecity():
	return render_template('/future/onecity.html')

