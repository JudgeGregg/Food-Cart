"""FoodCart."""
# vimfileencoding: utf-8
import urllib
import urllib2
import json

from google.appengine.ext import ndb
import webapp2
from webapp2_extras import sessions
import jsontemplate

from keys import API_KEY, SECRET_KEY

F2F_SEARCH_URL = 'http://food2fork.com/api/search'
F2F_GET_URL = 'http://food2fork.com/api/get'


MAIN_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html>
  <head>
    <title>Gregg's Recipes</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Bootstrap -->
    <link href="/bower_components/bootstrap/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Signin -->
    <link href="/static/css/signin.css" rel="stylesheet">

  </head>
  <body>
    <div class="container">
    <form class="form-signin" action="/search" method="post">
      <h2 class="form-signin-heading">Search Food</h2>
      <input type="text" name="name" class="form-control" placeholder="Name" required autofocus>
      <input type="text" name="search" class="form-control" placeholder="Recipe" required autofocus>
      <br>
      <button class="btn btn-lg btn-primary btn-block" type="submit">Grab</button>
    </form>
    </div>

    <!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
    <script src="/bower_components/jquery/jquery.js"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->
    <script src="/bower_components/bootstrap/dist/js/bootstrap.min.js"></script>
  </body>
</html>
"""

SEARCH_TEMPLATE = """
<!DOCTYPE html>
<html>
  <head>
    <title>Search Gregg's Recipes</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Bootstrap -->
    <link href="/bower_components/bootstrap/dist/css/bootstrap.min.css" rel="stylesheet">

  </head>
  <body>
    {.section recipes}
    <h2>Recipes</h2>

    <table width="100%">
    {.repeated section @}
        <tr>
        <td><a href="{source_url|htmltag}">Get to recipe</a>
        <td><i>{title}</i></td>
        <td>{publisher}</td>
        <td><a href="/ingredients/?recipe_id={recipe_id}">View ingredients</a>
        </td>
        </tr>
    {.end}
    </table>
    {.or}
    <p><em>(No page content matches)</em></p>
    {.end}
    <!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
    <script src="/bower_components/jquery/jquery.js"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->
    <script src="/bower_components/bootstrap/dist/js/bootstrap.min.js"></script>
  </body>
</html>
"""

GET_TEMPLATE = """
<!DOCTYPE html>
<html>
  <head>
    <title>Get Gregg's Recipes</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Bootstrap -->
    <link href="/bower_components/bootstrap/dist/css/bootstrap.min.css" rel="stylesheet">

  </head>
<body>
{.section recipe}
  <h2>{title}</h2>

  {.section ingredients}
  <table width="100%">
  {.repeated section @}
    <tr>
      <td><i>{@}</i></td>
    </tr>
  {.end}
    <!--<tr>
    <td><a href="/shoppinglist/?recipe_id={recipe_id}">Add ingredients to
    shopping list</a>
        </td>
    </tr>-->
  </table>
  <br/>
  {.end}
    <form action="/shoppinglist/" method="post">
        <input type="submit" value="Add to Shopping List" >
        <input type="hidden" name="recipe_id" value="{recipe_id}" >
    </form>
{.or}
  <p><em>(No page content matches)</em></p>
{.end}
    <!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
    <script src="/bower_components/jquery/jquery.js"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->
    <script src="/bower_components/bootstrap/dist/js/bootstrap.min.js"></script>
  </body>
</html>
"""


class SessionHandler(webapp2.RequestHandler):

    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()


class F2FMixin(object):

    def get_json_response(self, data, url):
        """@todo: Docstring for get_json_response

        :url: @todo
        :returns: @todo

        """
        encoded_data = urllib.urlencode(data)
        response = urllib2.urlopen(url, encoded_data)
        json_response = json.loads(response.read())
        return json_response

    def render_template(self, json_response, template):
        self.response.write(
            jsontemplate.expand(template, json_response))


class ShoppingList(ndb.Model):
    """Models an individual Guestbook entry with author, content, and date."""
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)


class MainPage(SessionHandler):
    """Application main page, with upload form."""
    def get(self):
        """GET method handler."""
        self.response.write(MAIN_PAGE_TEMPLATE)


class Search(SessionHandler, F2FMixin):
    """Application main page, with upload form."""

    def post(self):
        """POST method handler."""
        search = self.request.get('search')
        name = self.request.get('name')
        if not self.session.get('name'):
            self.session['name'] = name
        self.redirect('/search?' + search)

    def get(self):
        search = self.request.get('search')
        data = {'key': API_KEY, 'q': search}
        json_response = self.get_json_response(data, F2F_SEARCH_URL)
        self.render_template(json_response, SEARCH_TEMPLATE)


class Ingredients(SessionHandler, F2FMixin):
    RecipeDict = {}

    def get(self):
        """GET method handler."""
        recipe_id = self.request.get('recipe_id')
        data = {'key': API_KEY, 'rId': recipe_id}
        json_response = self.get_json_response(data, F2F_GET_URL)
        ingredients = json_response['recipe']['ingredients']
        self.session['recipes'][recipe_id] = ingredients
        self.session['kikoo'] = 'lol'
        self.render_template(json_response, GET_TEMPLATE)


class ShoppingList(SessionHandler, F2FMixin):
    """Docstring for ShoppingList """
    ShoppingList = {}

    def post(self):
        recipe_id = self.request.get('recipe_id')
        self.session['shoppinglist'].extend(self.session['recipes'][recipe_id])
        self.response.write(unicode(self.session['shoppinglist']))

    def get(self):
        recipe_id = self.request.get('recipe_id')
        self.session['shoppinglist'].extend(self.session['recipes'][recipe_id])
        self.response.write(unicode(self.session['shoppinglist']))

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': SECRET_KEY,
}

app = webapp2.WSGIApplication([
    ('/', MainPage), ('/search', Search), ('/ingredients/', Ingredients),
    ('/shoppinglist/', ShoppingList)], debug=True, config=config)
