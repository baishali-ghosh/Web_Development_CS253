#libraries imported
import os
import re
import random 
import hashlib
import hmac
from string import letters
from google.appengine.ext import db 
import webapp2
import jinja2
#jinja configuration
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
								extensions = ['jinja2.ext.autoescape'],
								autoescape = True)

#form VALIDATIONS
USER_RE = re.compile(r"^[a-zA-Z0-9-_]{3,20}$")#[]->types of character and {}->length
def valid_username(username):
	return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
	return password and PASS_RE.match(password)

MAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
def valid_mail(email):
	return not email or MAIL_RE.match(email)

#random string to secure cookie
secret = 'jusadwefHLqef249QMYNADasfas26234O2DSFHV9$#2'

def make_secure_val(val):
	return '%s|%s' % (val, hashlib.md5(secret + val).hexdigest())

def check_secure_val(secure_val):
	val = secure_val.split('|')[0]
	if secure_val == make_secure_val(val):
		return val

#rendering function definition	
def render_str(template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

class BaseHandler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		params['user'] = self.user
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template,**kw))

	def set_secure_cookie(self, name, val):
		cookie_val = make_secure_val(val)
		self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/' % (name, cookie_val))

	def read_secure_cookie(self, name):
		cookie_val = self.request.cookies.get(name)
		return cookie_val and check_secure_val(cookie_val)

	def login(self, user):
		self.set_secure_cookie('user_id', str(user.key().id()))

	def logout(self):
		self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')


	def initialize(self, *a, **kw):
		webapp2.RequestHandler.initialize(self, *a, **kw)
		uid = self.read_secure_cookie('user_id')
		self.user = uid and User.by_id(int(uid))

class MainPage(BaseHandler):
	def get(self):
		self.write('Type /signup in the url!')




#hashing function definitions
def make_salt():	
	y = ''
	for number in xrange(5):
		x = random.choice(letters)
		y = y + x
	return y

def make_pw_hash(name, pw, salt=None):
	if not salt:
		salt = make_salt()
	tohash = name + pw + salt
	hashval = hashlib.sha256(tohash).hexdigest()
	return "%s,%s" % (salt, hashval)

def valid_pw(name, password, h):
	salt = h.split(',')[0]
	return h == make_pw_hash(name, password, salt) 
#datastore entity kind decription
class User(db.Model):
	name = db.StringProperty(required=True)
	pw_hash = db.StringProperty(required=True)
	email = db.StringProperty()
	created = db.DateTimeProperty(auto_now_add = True)
	lastmodified = db.DateTimeProperty(auto_now = True)
	@classmethod
	def by_id(cls, uid):
		return User.get_by_id(uid)

	@classmethod
	def by_name(cls, name):
		u = db.GqlQuery('SELECT * FROM User WHERE name= :1', name)
		u = u.get()
		#u = User.all().filter('name=',  name).get()
		return u

	@classmethod
	def register(cls, name, pw, email=None):
		pw_hash = make_pw_hash(name, pw)
		return User(name = name,
						pw_hash = pw_hash,
						email = email)
	@classmethod
	def login(cls, name, pw):
		u = cls.by_name(name)
		if u and valid_pw(name, pw, u.pw_hash):
			return u


class SignUp(BaseHandler):
	
	def get(self):
		self.render('form.html')

	def post(self):
		have_error = False
		self.username = self.request.get('user')
		self.password = self.request.get('pass')
		self.verify = self.request.get('verpass')
		self.email = self.request.get('email')
		params = dict(username = self.username, email = self.email)
		if not valid_username(self.username):
			params['error_username'] = "Invalid Username."
			have_error = True
		if not valid_password(self.password):
			params['error_password'] = "Invalid Password."
			have_error = True
		elif self.request.get('pass') != self.verify:
			params['error_verify'] = "Passwords do not match!"
			have_error = True
		if not valid_mail(self.email):
			params['error_email'] = "Invalid email."
			have_error = True
		#print params
		if have_error:
			self.render('form.html', **params)
			
		else:
			self.done()
		def done(self, *a, **kw):
			raise NotImplentedError

class Register(SignUp):
	def done(self): #Overrides done of the SignUp handler
		u = User.by_name(self.username)
		if u:
			msg = 'Username already exists!'
			self.render('form.html', error_username = msg)
		else:
			u = User.register(self.username, self.password, self.email)
			u.put()
			self.login(u)
			self.redirect('/welcome')

class Login(BaseHandler):
	def get(self):
		self.render('login-form.html')
	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')
		u = User.login(username, password)
		if u:
			self.login(u)
			self.redirect('/welcome')
		else:
			msg = 'Invalid user'
			self.render('login-form.html', error= msg)	

class Logout(BaseHandler):
	def get(self):
		self.logout()
		self.redirect('/signup')

class WelcomeHandler(BaseHandler):
	def get(self):
		if self.user:
			#self.response.out.write('Welcome user!')
			self.render("welcome.html", username=self.user.name)
		else:
			self.redirect("/signup")
	
		 
application = webapp2.WSGIApplication([('/', MainPage),
									   ('/signup', Register),
									   ('/welcome', WelcomeHandler),
									   ('/login',Login),
									   ('/logout', Logout)],
										debug=True)