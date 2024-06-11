import os
import re
from urllib.parse import urlparse

import requests
from flask import Flask, jsonify, request
from lxml import html

EMAIL = os.environ['EMAIL']
PASSWORD = os.environ['PASSWORD']

XPATH_RE = "xpath\((.*)\)"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0"}

WEBSITES = {
    "www.mediapart.fr": {
        "login_url": "https://www.mediapart.fr/login_check",
        "login": {"email": EMAIL, "password": PASSWORD},
        "not_logged_in": "xpath(//div[contains(@class, 'paywall-login')])",
        "strip": ["xpath(//aside)", "xpath(//meta[@property='og:url'])", "xpath(//link[@rel='canonical'])"],
    },
    "www.monde-diplomatique.fr": {
        "login_url": "https://www.monde-diplomatique.fr/connexion/",
        "login": {
            "email": EMAIL,
            "mot_de_passe": PASSWORD,
            "valider": "Se+connecter",
            "session_remember": "oui",
            "formulaire_action": "identification_lecteur_ws",
            "retour": "https://www.monde-diplomatique.fr/",
            "email_nobot": "",
            "formulaire_action_args": "xpath(//form//input[@name='formulaire_action_args']/@value)",
            "_jeton": "xpath(//form//input[@name='_jeton']/@value)",
        },
        "not_logged_in": "xpath(//div[@id='paywall'])",
        "strip": ["xpath(/div[contains(@class, 'bandeautitre')])", "xpath(/div[contains(@class, 'bandeautitre')])", "xpath(//meta[@property='og:url'])", "xpath(//link[@rel='canonical'])"],
    },
}

app = Flask(__name__)

session = requests.Session()


@app.route("/fetch", methods=["GET"])
def fetch_url_content():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400

    key = urlparse(url).netloc

    response = session.get(url, headers=HEADERS)

    if key in WEBSITES and html.fromstring(response.content).xpath(re.search(XPATH_RE, WEBSITES[key]["not_logged_in"]).group(1)):
        tree = None
        login = dict(WEBSITES[key]["login"])

        for field in login.keys():
            if re.search(XPATH_RE, login[field]):
                if tree is None:
                    tree = html.fromstring(session.get(WEBSITES[key]["login_url"], headers=HEADERS).content)
                login[field] = tree.xpath(re.search(XPATH_RE, login[field]).group(1))[0]

        session.post(WEBSITES[key]["login_url"], data=login, headers=HEADERS)
        response = session.get(url, headers=HEADERS)

    content = response.content
    if "strip" in WEBSITES[key]:
        tree = html.fromstring(content)
        for strip in WEBSITES[key]["strip"]:
            for element in tree.xpath(re.search(XPATH_RE, strip).group(1)):
                element.getparent().remove(element)

        content = html.tostring(tree, encoding=str)

    return content


if __name__ == "__main__":
    app.run(debug=True)
