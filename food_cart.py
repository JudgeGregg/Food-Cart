"""FoodCart."""
# -*- coding: utf8 -*-
import urllib
import urllib2
import json
import logging

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
        <!--<td><a href="/ingredients/{recipe_id|htmltag}">Add ingredients to
        shopping list</a>-->
        <td><form action="/ingredients" method="post">
        <input type="hidden" name="r_id" value={recipe_id}>
        <input type="submit" value="Add to Shopping List">
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
{.or}
  <p><em>(No page content matches)</em></p>
{.end}
  </body>
</html>
"""


class MainPage(webapp2.RequestHandler):
    """Application main page, with upload form."""

    def get(self):
        """GET method handler."""
        self.response.write(MAIN_PAGE_HTML)


class Search(webapp2.RequestHandler):
    """Application main page, with upload form."""

    def post(self):
        """POST method handler."""
        content = self.request.get('content')
        data = {'key': API_KEY, 'q': content}
        encoded_data = urllib.urlencode(data)
        response = urllib2.urlopen(F2F_SEARCH_URL, encoded_data)
        json_response = json.loads(response.read())
        self.response.write(
            jsontemplate.expand(SEARCH_TEMPLATE, json_response))


class Ingredients(webapp2.RequestHandler):
    ingredients = []

    def post(self):
        """POST method handler."""
        recipe_id = self.request.get('r_id')
        import pdb; pdb.set_trace()
        data = {'key': API_KEY, 'rId': recipe_id}
        encoded_data = urllib.urlencode(data)
        response = urllib2.urlopen(F2F_GET_URL, encoded_data)
        json_response = json.loads(response.read())
        logging.info(recipe_id)
        self.response.write(
            jsontemplate.expand(SEARCH_TEMPLATE, json_response))

app = webapp2.WSGIApplication([
    ('/', MainPage), ('/search', Search), ('/ingredients', Ingredients)],
    debug=True)
