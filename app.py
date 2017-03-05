import os
import random

import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

DEBUG = os.environ.get('DEBUG', False) in ('true', '1', 'y', 'yes')
app.debug = DEBUG

_UAS = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_7) AppleWebKit/601.7.7 '
    '(KHTML, like Gecko) Version/9.1.2 Safari/601.7.7',

    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:46.2) '
    'Gecko/20100101 Firefox/46.1',

    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',

    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:48.0) Gecko/20100101 '
    'Firefox/48.1',

    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:51.1) Gecko/20100101 '
    'Firefox/51.1',
)

def realistic_request(
    url,
    verify=True,
    no_user_agent=False,
    allow_redirect=True
):
    headers = {
        'Accept': (
            'text/html,application/xhtml+xml,application/xml,text/xml'
            ';q=0.9,*/*;q=0.8'
        ),
        'User-Agent': random.choice(_UAS),
        'Accept-Language': 'en-US,en;q=0.5',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }
    if no_user_agent:
        headers.pop('User-Agent')
    response = requests.get(
        url, headers=headers, verify=verify, allow_redirects=False
    )
    if response.status_code == 302 or response.status_code == 301:
        if allow_redirect:
            return realistic_request(
                url,
                verify=verify,
                no_user_agent=no_user_agent,
                allow_redirect=False
            )
    return response


@app.route("/")
def index():
    return "Hello World"


@app.route('/download', methods=['POST'])
def download():
    url = request.args.get('url')
    assert url
    assert '://' in url
    r = realistic_request(url)
    if r.status_code != 200:
        return jsonify({
            'url': url,
            'status_code': r.status_code,
        })
    return jsonify({
        'url': url,
        'html': r.content.decode('utf-8'),
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
