"""FoodCart."""
# -*- coding: utf8 -*-
import urllib
import urllib2
import json

import webapp2
import jsontemplate

API_KEY = 'secret'
F2F_SEARCH_URL = 'http://food2fork.com/api/search'
F2F_GET_URL = 'http://food2fork.com/api/get'


MAIN_PAGE_HTML = """
<html>
  <body>
    <form action="/search" method="post">
      <div><textarea name="content" rows="3" cols="60"></textarea></div>
      <div><input type="submit" value="Search Food"></div>
    </form>
  </body>
</html>
"""

SEARCH_TEMPLATE = """
<html>
  <body>
    {.section recipes}
    <h2>Recipes</h2>

    <table width="100%">
    {.repeated section @}
        <tr>
        <td><a href="{source_url|htmltag}">Get to recipe</a>
        <td><i>{title}</i></td>
        <td>{publisher}</td>
        <td>{recipe_id}</td>
        <td><a href="/ingredients/?recipe_id={recipe_id}">Add ingredients to
        shopping list</a>
        </td>
        </tr>
    {.end}
    </table>
    {.or}
    <p><em>(No page content matches)</em></p>
    {.end}
  </body>
</html>
"""

GET_TEMPLATE = """
<html>
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
  </table>
  {.end}
    <form action="/shoppinglist" method="post">
        <input type="submit" value="Add to Shopping List" >
        <input type="hidden" name="recipe_id" value="{recipe_id}" >
    </form>
{.or}
  <p><em>(No page content matches)</em></p>
{.end}
  </body>
</html>
"""


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


class MainPage(webapp2.RequestHandler):
    """Application main page, with upload form."""

    def get(self):
        """GET method handler."""
        self.response.write(MAIN_PAGE_HTML)


class Search(webapp2.RequestHandler, F2FMixin):
    """Application main page, with upload form."""

    def post(self):
        """POST method handler."""
        content = self.request.get('content')
        data = {'key': API_KEY, 'q': content}
        json_response = self.get_json_response(data, F2F_SEARCH_URL)
        self.render_template(json_response, SEARCH_TEMPLATE)


class Ingredients(webapp2.RequestHandler, F2FMixin):
    RecipeDict = {}

    def get(self):
        """GET method handler."""
        recipe_id = self.request.get('recipe_id')
        data = {'key': API_KEY, 'rId': recipe_id}
        json_response = self.get_json_response(data, F2F_GET_URL)
        ingredients = json_response['recipe']['ingredients']
        Ingredients.RecipeDict[recipe_id] = ingredients
        self.render_template(json_response, GET_TEMPLATE)


class ShoppingList(webapp2.RequestHandler, F2FMixin):
    """Docstring for ShoppingList """
    Ingredients = []

    def post(self):
        recipe_id = self.request.get('recipe_id')
        ingredients = Ingredients.RecipeDict[recipe_id]
        ShoppingList.Ingredients.extend(ingredients)
        self.response.write(ShoppingList.Ingredients)


app = webapp2.WSGIApplication([
    ('/', MainPage), ('/search', Search), ('/ingredients/', Ingredients),
    ('/shoppinglist', ShoppingList)], debug=True)
