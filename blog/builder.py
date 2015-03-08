import os
import sys
import shutil
import glob

from .parser import Parser
from .tokenizer import Tokenizer

class Builder(object):

    def __init__(self):
        self.articles = []
        self.source_root = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            ".."
        )
        self.static_root = os.path.join(self.source_root, "static")
        self.content_root = os.path.join(self.source_root, "content")
        self.template_root = os.path.join(self.source_root, "templates")

        self.target = os.path.join(self.source_root, "out")

    def sort_articles(self):
        self.articles = sorted(self.articles,
                               key=lambda k: k['date'],
                               reverse=True)

    def render(self, template, **kwargs):
        val = ""
        with open(os.path.join(self.template_root, template)) as fp:
            val = fp.read().format(**kwargs)
            return val

    def save_page(self, name, content):
        with open(os.path.join(self.target, name), "w") as fp:
            fp.write(content)

    def render_content(self):
        for blog in glob.glob(os.path.join(self.content_root, "*.blog")):
            title = os.path.basename(blog).split(".")[0].replace("-", " ").title()
            fname = os.path.basename(blog).split(".")[0]+".html"
            content = ""
            with open(blog) as fp:
                tokenizer = Tokenizer()
                tokens = tokenizer.tokenize(fp.read())
                parser = Parser(tokens)
                parser.parse()
                content = parser.output
                entry = parser.attributes
                entry["name"] = title
                entry["url"] = "/" + fname
                self.articles.append(entry)
                rendered_content = self.render("blog.html",
                                               blog=content,
                                               attributes=parser.attributes)
                rendered_content = self.render("base.html", title=title,
                                               body=rendered_content)
                self.save_page(fname, rendered_content)

    def render_index(self):
        self.sort_articles()
        latest = "<ul>"
        for article in self.articles[:5]:
            latest += "<li><a href=\"{article[url]}\">{article[name]}</a>, <em>{article[date]}</em></li>".format(article=article)
        latest += "</ul>"
        content = self.render("index.html",
                              latest_articles=latest)
        page = self.render("base.html",
                           title="Juhani Imberg",
                           body=content)
        self.save_page("index.html", page)

    def build(self):
        shutil.rmtree(self.target, ignore_errors=True)
        shutil.copytree(self.static_root, self.target)
        self.render_content()
        self.render_index()
