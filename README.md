Spotify token
===
Command line tool to get an access token for the spotify web api. Note that this tool dose not include security
features like the states property and should only be used for personal use!

## Usage
1. Install the requirements: \
`python3 -m pip install -r requirements.txt`
2. Run in with `python3 spotify-token.py` and follow the instructions.

Note: You need to create an app at https://developer.spotify.com/dashboard. You can find the credentials in the
app settings. The redirect_uri must be `http://localhost:{YOUR_PORT}/callback` to work.