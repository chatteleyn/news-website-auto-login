import base64
import os
import re
from urllib.parse import urlparse

import requests
from flask import Flask, jsonify, request
from lxml import etree

EMAIL = os.environ['EMAIL']
PASSWORD = os.environ['PASSWORD']

XPATH_RE = r"xpath\((.*)\)"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0"}

COOKIES = {"cc": "{%22disagreement%22:[]%2C%22creation%22:1718058094440%2C%22update%22:1718058096681}"}

LOGINS = {
    "www.mediapart.fr": {
        "login_url": "https://www.mediapart.fr/login_check",
        "login": {"email": EMAIL, "password": PASSWORD},
        "not_logged_in": "xpath(//div[contains(@class, 'paywall-login')])",
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
    },
}

app = Flask(__name__)

session = requests.Session()


@app.route("/fetch", methods=["GET"])
def fetch_url_content():
    url_base64 = request.args.get("url")
    url = base64.b64decode(url_base64.encode("ascii")).decode("ascii")
    print(url)
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400

    key = urlparse(url).netloc

    response = session.get(url, headers=HEADERS, cookies=COOKIES)

    if key in LOGINS and etree.HTML(response.content).xpath(re.search(XPATH_RE, LOGINS[key]["not_logged_in"]).group(1)):
        tree = None
        login = LOGINS[key]["login"]

        for field in login.keys():
            if re.search(XPATH_RE, login[field]):
                if tree is None:
                    tree = etree.HTML(session.get(LOGINS[key]["login_url"], headers=HEADERS, cookies=COOKIES).content)
                login[field] = tree.xpath(re.search(XPATH_RE, login[field]).group(1))

        session.post(LOGINS[key]["login_url"], data=login, headers=HEADERS)
        response = session.get(url, headers=HEADERS, cookies=COOKIES)

    return response.content


if __name__ == "__main__":
    app.run()
