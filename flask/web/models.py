# Here are models for database

from flask.ext.login import UserMixin

ROLE_USER = 0
ROLE_ADMIN = 1

class User(UserMixin):
	# id = db.Column(db.Integer, primary_key = True)
	# unique_id = db.Column(db.Integer, index = True, unique = True)
	# email = db.Column(db.String(120), index = True, unique = True)
	# first_name = db.Column(db.String(64), index = True)
	# last_name = db.Column(db.String(64), index = True)
	# role = db.Column(db.SmallInteger, default = ROLE_USER)

	def __init__(self, parse_id, auth_id, email, first_name, last_name, role_assigned='USER'):
		self.id = parse_id
		self.unique_id = auth_id
		self.email = email
		self.first_name = first_name
		self.last_name = last_name
		self.role = role_assigned

	def __repr__(self):
		return '<User %r>' % (self.first_name)

	def is_admin(self):
		return self.role == 'ADMIN'

	# These four methods are for Flask-Login
	def is_authenticated(self):
		return True
 
	def is_active(self):
		return True
 
	def is_anonymous(self):
		return False
 
	def get_id(self):
		# print 'getting id returns: ' + unicode(self.id)
		return unicode(self.id)

