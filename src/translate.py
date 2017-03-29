from http import client
from urllib import parse
import json


API_KEY = "trnsl.1.1.20170325T133003Z.195935bd46ed78fe.cf328997346a519b7688bff809c0075e2cdbc579"
API_SERVER = "translate.yandex.net"
API_URL = "/api/v1.5/tr.json/translate"


def makeURL(lang, text):
    encoded = parse.urlencode({'text': text, })
    return "{}?key={}&lang={}&{}".format(API_URL, API_KEY, lang, encoded)


def translate(src, dest, text):
    conn = client.HTTPSConnection(API_SERVER)
    conn.request("GET", makeURL(dest, text))
    response = conn.getresponse().read().decode('utf-8-sig')
    decoded = json.loads(response)

    txt = decoded.get('text', [''])
    return {
        'text': txt[0],
    }
