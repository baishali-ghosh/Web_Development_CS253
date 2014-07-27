import cgi
import webapp2

form = """
		<html>
		<head><title>Testing form</title></head>
		<body>
		<h2>Enter text to ROT13! </h2>
		<form action="/testform" method="post">
		<textarea name="q"> </textarea>
		<br>
		<input type="submit">
		</form>
		</body>
		</html>

	    """
class MainPage(webapp2.RequestHandler):
	def get(self):
		self.response.out.write(form)

class TestHandler(webapp2.RequestHandler):
	def post(self):
		q = self.request.get('q')
		self.response.out.write("You entered: <br>")	
		self.response.out.write(cgi.escape(q))
		#store the rot13ed text then display it.
		text = q.encode('rot13')
		self.response.out.write("<br>The text when ROT13ed is: <br>")		
		self.response.out.write(cgi.escape(text))

application = webapp2.WSGIApplication([('/', MainPage),
									   ('/testform', TestHandler)],
										debug=True)