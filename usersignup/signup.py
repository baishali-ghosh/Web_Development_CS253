#libraries imported
import re
import os
import urllib
from google.appengine.api import users
from google.appengine.ext import db 
import webapp2
import jinja2
#jinja configuration
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
								extensions = ['jinja2.ext.autoescape'],
								autoescape = True)

#VALIDATIONS
USER_RE = re.compile(r"^[a-zA-Z0-9-_]{3,20}$")#[]->types of character and {}->length
def valid_username(username):
	return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
	return password and PASS_RE.match(password)

MAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
def valid_mail(email):
	return not email or MAIL_RE.match(email)

#rendering function definition	
def render_str(template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

class BaseHandler(webapp2.RequestHandler):
	def render(self, template, **kw):
		self.response.out.write(render_str(template,**kw))

#	def write(self, *a, **kw):
#		self.response.out.write(*a, **kw)


class MainPage(BaseHandler):
	
	def get(self):
		self.render('newpost.html')

	def post(self):
		have_error = False
		user = valid_username(self.request.get('user'))
		pasw = valid_password(self.request.get('pass'))
		vpass = self.request.get('verpass')
		email = valid_mail(self.request.get('email'))
		params = dict(username = self.request.get('user'), email = self.request.get('email'))
		if not (user):
			params['error_username'] = "Invalid Username."
			have_error = True
		if not (pasw):
			params['error_password'] = "Invalid Password."
			have_error = True
		elif self.request.get('pass') != vpass:
			params['error_verify'] = "Passwords do not match!"
			have_error = True
		if not email:
			params['error_email'] = "Invalid email."
			have_error = True
		us = self.request.get('user')
		#print params
		if have_error:
			self.render('form.html', **params)
		else:
			self.redirect("/welcome?user=" + us )


class WelcomeHandler(BaseHandler):
	def get(self):
		urluser = self.request.get('user')
		if valid_username(urluser):
			self.render("welcome.html", username=urluser)
		else:
			self.redirect("/")
	
		 
application = webapp2.WSGIApplication([('/', MainPage),
									   ('/welcome', WelcomeHandler)],
										debug=True)