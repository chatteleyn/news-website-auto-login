import json
import os
import re
from urllib.parse import unquote, urljoin, urlparse

import requests
from flask import Flask, request
from lxml import html

# Regex for an xpath
XPATH_RE = "^xpath\((.*)\)$"

# User-Agent to injex when doing requests
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0"}

# Load the config file
with open("website_config.json", "r") as config_file:
    config_string = config_file.read()
    # Replace the environment variables with their values
    CONFIG = json.loads(re.sub("\$(\S+)\$", lambda match: os.environ.get(match.group(1)), config_string))

app = Flask(__name__)

session = requests.Session()


def remove_html_elements(tree, elements=[]):
    for strip in elements:
        for element in tree.xpath(strip):
            element.getparent().remove(element)

    return tree


def move_html_elements(tree, elements=[]):
    for origin, target, pos in elements:
        print(origin, target, pos)
        origin_element = tree.xpath(origin)[0]
        parent = origin_element.getparent()
        if parent is not None:
            parent.remove(origin_element)

        target_element = tree.xpath(target)[0]
        if pos == "inside-up":
            target_element.insert(0, origin_element)
        elif pos == "inside-bottom":
            target_element.append(origin_element)
        elif pos == "outside-up":
            parent = target_element.getparent()
            if parent is not None:
                index = parent.index(target_element)
                parent.insert(index, origin_element)
        elif pos == "outside-bottom":
            target_parent = target_element.getparent()
            if target_parent is not None:
                index = target_parent.index(target_element)
                target_parent.insert(index + 1, origin_element)

    return tree


def replace_relative_links(tree, parsed_url):
    for img in tree.xpath("//img"):
        src = img.get("src")
        if src and not src.startswith(("http://", "https://")):
            absolute_src = urljoin(parsed_url.scheme + "://" + parsed_url.netloc, src)
            img.set("src", absolute_src)

    for a in tree.xpath("//a"):
        href = a.get("href")
        if href and not href.startswith(("http://", "https://")):
            absolute_href = urljoin(parsed_url.scheme + "://" + parsed_url.netloc, href)
            a.set("href", absolute_href)

    return tree


@app.route("/", methods=["GET"])
def fetch_url_content():
    url_encoded = request.args.get("url")
    if not url_encoded:
        return r"You need to specify an url with ?url=URL-ENCODED", 400
    url = unquote(url_encoded)
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
    if key in CONFIG and "strip" in CONFIG[key]:
        response_tree = remove_html_elements(response_tree, [re.search(XPATH_RE, element).group(1) for element in CONFIG[key]["strip"]])

    # Move content from the HTML
    if key in CONFIG and "move" in CONFIG[key]:
        response_tree = move_html_elements(
            response_tree,
            [(re.search(XPATH_RE, element[0]).group(1), re.search(XPATH_RE, element[1]).group(1), element[2]) for element in CONFIG[key]["move"]],
        )

    # Replace relative image sources to absolute links
    response_tree = replace_relative_links(response_tree, parsed_url)

    content = html.tostring(response_tree, encoding="utf-8")

    return content


if __name__ == "__main__":
    app.run()
