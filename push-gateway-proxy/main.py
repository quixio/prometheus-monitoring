from flask import Flask, request, Response
import requests
import os

app = Flask(__name__)

PUSHGATEWAY_URL = os.getenv("PUSHGATEWAY_URL")
BASIC_AUTH_USER = os.getenv("BASIC_AUTH_USER")
BASIC_AUTH_PASS = os.getenv("BASIC_AUTH_PASS")

# Authenticate requests
def authenticate(req):
    auth = req.authorization
    return auth and auth.username == BASIC_AUTH_USER and auth.password == BASIC_AUTH_PASS

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    if not authenticate(request):
        return Response('Authentication required', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

    # Forward request to Pushgateway
    resp = requests.request(
        method=request.method,
        url=f"{PUSHGATEWAY_URL}/{path}",
        headers={key: value for key, value in request.headers if key.lower() != 'host'},
        data=request.get_data(),
        params=request.args,
        allow_redirects=False,
    )

    # Send response back to client
    excluded_headers = ['content-encoding', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    response = Response(resp.content, resp.status_code, headers)
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)