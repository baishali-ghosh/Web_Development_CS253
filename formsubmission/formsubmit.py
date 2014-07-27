import cgi
import webapp2
form = """      <form action="/testform" method="post">
		<input type="text" name="q"> 
		<input type="submit">
		</form>"""

class MainPage(webapp2.RequestHandler):
	def get(self):
		self.response.out.write(form)

class TestHandler(webapp2.RequestHandler):
	def post(self):
		q = self.request.get('q')
		self.response.out.write("<html><body> You entered: <pre>")	
		self.response.out.write(cgi.escape(q))
		self.response.out.write("</pre></body></html>")			

application = webapp2.WSGIApplication([('/', MainPage),
									   ('/testform', TestHandler)],
										debug=True)
