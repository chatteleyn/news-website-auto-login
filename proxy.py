import json
import os
import re
from urllib.parse import unquote, urljoin, urlparse

import requests
from flask import Flask
from lxml import html

# Regex for an xpath
XPATH_RE = "xpath\((.*)\)"

# User-Agent to injex when doing requests
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0"}

# Load the config file
with open("website_config.json", "r") as config_file:
    config_string = config_file.read()
    # Replace the environment variables with their values
    CONFIG = json.loads(re.sub("\$(.*?)\$", lambda match: os.environ.get(match.group(1)), config_string))

app = Flask(__name__)

session = requests.Session()


@app.route("/<path:encoded_url>", methods=["GET"])
def fetch_url_content(encoded_url):
    url = unquote(encoded_url)
    parsed_url = urlparse(url)
    key = parsed_url.netloc

    response = session.get(url, headers=HEADERS)

    # If website is in the config and not logged in
    if key in CONFIG and html.fromstring(response.content).xpath(re.search(XPATH_RE, CONFIG[key]["not_logged_in"]).group(1)):
        tree = None
        login = dict(CONFIG[key]["login"])

        for field in login.keys():
            # Check if the field is an xpath and retrive the value from the HTML
            if re.search(XPATH_RE, login[field]):
                if tree is None:
                    tree = html.fromstring(session.get(CONFIG[key]["login_url"], headers=HEADERS).content)
                login[field] = tree.xpath(re.search(XPATH_RE, login[field]).group(1))[0]

        # Login by injecting data info in a POST
        session.post(CONFIG[key]["login_url"], data=login, headers=HEADERS)
        response = session.get(url, headers=HEADERS)

    content = response.content
    response_tree = html.fromstring(content)

    # Strip content from the HTML
    if "key" in CONFIG and "strip" in CONFIG[key]:
        for strip in CONFIG[key]["strip"]:
            for element in response_tree.xpath(re.search(XPATH_RE, strip).group(1)):
                element.getparent().remove(element)

    # Replace relative image sources to absolute links
    for img in response_tree.xpath("//img"):
        src = img.get("src")
        if src and not src.startswith(("http://", "https://")):
            absolute_src = urljoin(parsed_url.scheme + "://" + parsed_url.netloc, src)
            img.set("src", absolute_src)

    content = html.tostring(response_tree, encoding="utf-8")

    return content


if __name__ == "__main__":
    app.run()
