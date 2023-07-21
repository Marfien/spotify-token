import threading
import webbrowser

import inquirer
import requests
from urllib.parse import parse_qs, urlencode
from http.server import BaseHTTPRequestHandler, HTTPServer

# webserver settings
HOST_ADDRESS = 'localhost'
PORT = 8080
REDIRECT_URI_PATH = '/callback'
DEBUG = False

AVAILABLE_SCOPES = [
    'ugc-image-upload',
    'user-read-playback-state',
    'user-modify-playback-state',
    'user-read-currently-playing',
    'app-remote-control',
    'streaming',
    'playlist-read-private',
    'playlist-read-collaborative',
    'playlist-modify-private',
    'playlist-modify-public',
    'user-follow-modify',
    'user-follow-read',
    'user-read-playback-position',
    'user-top-read',
    'user-read-recently-played',
    'user-library-modify',
    'user-library-read',
    'user-read-email',
    'user-read-private',
    'user-soa-link',
    'user-soa-unlink',
    'user-manage-entitlements',
    'user-manage-partner',
    'user-create-partner'
]


def get_auth_url():
    auth_params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': f'http://{HOST_ADDRESS}:{PORT}{REDIRECT_URI_PATH}',
        'scope': SELECTED_SCOPES,
    }
    auth_url = 'https://accounts.spotify.com/authorize?' + urlencode(auth_params)
    return auth_url


def get_access_and_refresh_token(authorization_code):
    # Access Token erhalten
    token_url = 'https://accounts.spotify.com/api/token'
    token_data = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': f'http://{HOST_ADDRESS}:{PORT}{REDIRECT_URI_PATH}',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }

    response = requests.post(token_url, data=token_data)
    if response.status_code == 200:
        json = response.json()
        return json['access_token'], json['refresh_token']

    print(f'Error: Request unsuccessful. Status code: {response.status_code}.')
    return None


class Number(inquirer.Text):

    def __init__(self, name, message="", default=None, **kwargs):
        super().__init__(name, message, default, **kwargs)

    def validate(self, current):
        return super().validate(current) and str(current).isdigit()


# Handle http callback
class SpotifyAuthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self.send_response(302)
            self.send_header('Location', get_auth_url())
            self.end_headers()
        elif not self.path.startswith(REDIRECT_URI_PATH):
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Error: Page not found')

        query_params = parse_qs(self.path.split('?', 1)[1])
        authorization_code = query_params.get('code', [''])[0]

        if not authorization_code:
            return

        access_token, refresh_token = get_access_token(authorization_code)

        if not access_token:
            return

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write('You can close this tap now. Continue back in console.'.encode())
        self.wfile.flush()

        threading.Thread(target=WEB_SERVER.shutdown).start()
        input('Press enter to show tokens...')
        print(f'Access Token: {access_token}')
        print(f'Refresh Token: {refresh_token}')
    
    def log_request(self, code: int | str = ..., size: int | str = ...) -> None:
        if not DEBUG:
            return
        
        super().log_request(code=code, size=size)


def main():
    global WEB_SERVER
    global CLIENT_ID
    global CLIENT_SECRET
    global SELECTED_SCOPES
    global PORT

    args = inputs()

    PORT = int(args['port'])
    CLIENT_ID = args['client_id']
    CLIENT_SECRET = args['client_secret']
    SELECTED_SCOPES = ' '.join(args['scopes'])

    WEB_SERVER = HTTPServer((HOST_ADDRESS, PORT), SpotifyAuthHandler)
    print(f'Server is running on "{HOST_ADDRESS}:{PORT}".')
    print(f'Trying to open "http://{HOST_ADDRESS}:{PORT}" in browser...')
    webbrowser.open_new_tab(url=f'http://{HOST_ADDRESS}:{PORT}')
    WEB_SERVER.serve_forever()


def inputs():
    questions = [
        inquirer.Text(
            name='client_id',
            message='Your client id'
        ),
        inquirer.Password(
            name='client_secret',
            message='Your client secret'
        ),
        inquirer.Checkbox(
            name='scopes',
            message='Select scopes (with SPACE)',
            choices=AVAILABLE_SCOPES
        ),
        Number(
            name='port',
            message='Webserver port',
            default=PORT
        )
    ]

    return inquirer.prompt(questions)


if __name__ == '__main__':
    main()
