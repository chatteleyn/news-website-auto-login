from urllib.parse import urlparse

import requests
from lxml import etree
from flask import Flask, jsonify, request
import re

XPATH_RE = "xpath\((.*)\)"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0"}

app = Flask(__name__)

session = requests.Session()


@app.route("/fetch", methods=["GET"])
def fetch_url_content():
    return """<!doctype html>
<html>
<head>
<META NAME="ROBOTS" CONTENT="NOINDEX, NOFOLLOW">
<meta charset="utf-8">

<title>Original article title</title>
</head>

<body>
<article class="film_review">
<header>
<h2>some subtitle</h2>
</header>
<section class="main_review">
<p>copy of article I want to read</p>
</section>

<footer>
<p>
Posted on
<time datetime="2015-05-15 19:00">May 15</time>
by Staff.
</p>
</footer>
</article>
</body>
</html>"""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
