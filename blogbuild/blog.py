#libraries imported
import re
import os
import urllib
from google.appengine.api import users
from google.appengine.ext import db 
import webapp2
import jinja2
from random import randint
#jinja configuration
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
								extensions = ['jinja2.ext.autoescape'],
								autoescape = True)

#rendering function definition	

def render_str(template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

class BaseHandler(webapp2.RequestHandler):
	#def write(self, *a, **kw):
	#	self.response.out.write(*a, **kw)

	def render(self, template, **kw):
		self.response.out.write(render_str(template,**kw))

####Blog Area######
def blog_key(name = 'default'):
	return db.Key.from_path('blogs', name)
#database creation
class Post(db.Model):
	posttitle = db.StringProperty(required = True)
	postcontent = db.TextProperty(required = True)
	postcreated = db.DateTimeProperty(auto_now_add = True)
	last_modified = db.DateTimeProperty(auto_now = True)

	def render(self):
		self._render_text = self.postcontent.replace('\n', '<br>')
		return render_str('post.html', p=self)

#Front of blog with 10 mos
class BlogView(BaseHandler):
	def get(self):
		posts = db.GqlQuery('SELECT * FROM Post ORDER BY postcreated DESC LIMIT 10') 
		self.render('front.html', posts = posts)

#Displays the permalink page for the blog entry
class PermaPage(BaseHandler):
	def get(self, post_id):
		key = db.Key.from_path('Post', int(post_id), parent=blog_key())
		post = db.get(key)
		if not post:
			self.error(404)
			return
		self.render('permalink.html', post = post)
#create a newpost
class NewPost(BaseHandler):
	
	def get(self):
		self.render('newpost.html')
	def post(self):
		title = self.request.get('blogtitle')
		postbody = self.request.get('blogbody')
		params = dict(title = title, body = postbody)
		have_error = False
		if not (title):
			params['error_title'] = "Your post needs a title!"
			have_error = True 
		if not (postbody):
			params['error_post'] = "Your post requires content!"
			have_error = True
		if have_error:
			self.render('newpost.html', **params)
		else:
			#if both title and post are present create the database entry
			p = Post(parent = blog_key(), posttitle = title, postcontent = postbody)
			p.put()
			self.redirect('/blog/%s' % str(p.key().id()))


		
application = webapp2.WSGIApplication([('/blog/newpost', NewPost),
									   ('/blog/?', BlogView),
									   ('/blog/([0-9]+)', PermaPage)], #anything in() in the url gets passed as a parameter to the corrsponding handler
										debug=True)