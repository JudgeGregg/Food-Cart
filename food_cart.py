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
<script src="//ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
<script type=text/javascript>
function add_to_shopping_list() {
    $('#hiddenfield')[0].value = JSON.stringify($('#mydiv')[0].data-json);
    $('#myform').submit();
}
</script>
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
    <form id="myform" action="/shoppinglist" method="post">
        <input type="button" value="Add to Shopping List" onclick="add_to_shopping_list()">
        <input id="hiddenfield" type="hidden" name="ingredients">
    </form>
  <div id="mydiv" style="visibility:hidden" data-json="{ingredients}">TEST</div>
  {.end}
{.or}
  <p><em>(No page content matches)</em></p>
{.end}
  </body>
</html>
"""


class F2FMixin(object):

    def render_template(self, data, url, template):
        encoded_data = urllib.urlencode(data)
        response = urllib2.urlopen(url, encoded_data)
        json_response = json.loads(response.read())
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
        self.render_template(data, F2F_SEARCH_URL, SEARCH_TEMPLATE)


class Ingredients(webapp2.RequestHandler, F2FMixin):

    def get(self):
        """GET method handler."""
        recipe_id = self.request.get('recipe_id')
        data = {'key': API_KEY, 'rId': recipe_id}
        self.render_template(data, F2F_GET_URL, GET_TEMPLATE)


class ShoppingList(webapp2.RequestHandler, F2FMixin):
    """Docstring for ShoppingList """
    Ingredients = []

    def post(self):
        ingredients = self.request.get('ingredients')
        import pdb; pdb.set_trace()
        ShoppingList.Ingredients.extend(ingredients)
        self.response.write(ShoppingList.Ingredients)


app = webapp2.WSGIApplication([
    ('/', MainPage), ('/search', Search), ('/ingredients/', Ingredients),
    ('/shoppinglist', ShoppingList)], debug=True)
