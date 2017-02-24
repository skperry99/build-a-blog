#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title = db.StringProperty(required = True)
    entry = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def render_frontpage(self, title='', entry='', error=''):
        entries = db.GqlQuery("SELECT * FROM Blog "
                            "ORDER BY created DESC "
                            "LIMIT 5 ")

        self.render("frontpage.html", title=title, entry=entry, error=error, entries=entries)

    def get(self):
        self.render_frontpage()

    def post(self):
        title = self.request.get("title")
        entry = self.request.get("entry")

        if title and entry:
            p = Blog(title=title, entry=entry)
            p.put()

            self.redirect("/")
        else:
            error = "Please enter a title and a blog entry"
            self.render_frontpage(title, entry, error)

class WholeBlogHandler(Handler):
    def render_blogpage(self, title='', entry='', error=''):
        entries = db.GqlQuery("SELECT * FROM Blog "
                            "ORDER BY created DESC ")

        self.render("blogpage.html", title=title, entry=entry, error=error, entries=entries)

    def get(self):
        self.render_blogpage()

class NewPostHandler(Handler):
    def render_newpost(self, title='', entry='', error=''):
        self.render("newpost.html", title=title, entry=entry, error=error)

    def get(self):
        self.render_newpost()

    def post(self):
        title = self.request.get("title")
        entry = self.request.get("entry")

        if title and entry:
            p = Blog(title=title, entry=entry)
            p.put()
            new_id = p.key().id()
            path = "/blog/"+str(new_id)

            self.redirect(path)
        else:
            error = "Please enter a title and a blog entry"
            self.render_newpost(title, entry, error)

class ViewPostHandler(Handler):
    def render_view_post(self, entry_id, error=''):
        blog = Blog.get_by_id(int(entry_id))
        if not blog:
            error = "Something went wrong"
            self.redirect("/", error)

        else:
            self.render("view_post.html", blog=blog)

        #t = jinja2.get_template('view_post.html')
        #content = t.render(entry=entry)

    def get(self, entry_id):
        self.render_view_post(entry_id)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blogpage', WholeBlogHandler),
    ('/newpost', NewPostHandler),
    webapp2.Route('/blog/<entry_id:\d+>', ViewPostHandler),
], debug=True)
