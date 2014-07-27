import os
import webapp2
import jinja2
#jinja configuration
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
								extensions = ['jinja2.ext.autoescape'],
								autoescape = True)
def render_str(template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

class BaseHandler(webapp2.RequestHandler):
	def render(self, template, **kw):
		self.response.out.write(render_str(template,**kw))

	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

class MainPage(BaseHandler):
	def get(self):
		 self.response.headers['Content-type'] = 'text/plain'
		 visits = self.request.cookies.get('visits', 0)
		 if visits.isdigit(): 
		 	visits = int(visits) + 1
		 else:
		 	visits = 0
		 self.response.headers.add_header('Set-Cookie', 'visits=%s' % visits)
		 if visits > 100:
		 	self.write("You are the best ever!")
		 else:
		 	self.response.out.write("You've been here %s times! " % visits)

application = webapp2.WSGIApplication([('/', MainPage)], debug=True)