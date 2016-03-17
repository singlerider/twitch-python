import json
import os
import sqlite3 as lite
from config import (twitch_client_id, twitch_client_secret,
                    twitch_redirect_uri, twitch_scopes)

import requests
from flask import Flask, json, redirect, request, session
from flask.ext.cors import CORS
from requests_oauthlib import OAuth2Session


class Twitch:

    def __init__(self, channel, user):  # require these two for instantiation
        self.channel = channel
        self.user = user

    # this endpoint fails often
    def users(self):
        n = 0
        dummy = {  # in case the endpoint fails (can be as often as 1:8)
            "_links": {}, "chatters_count": 0, "chatters": {
                "staff": [], "admin": [], "global_mods": [],
                "viewers": [], "moderators": []}}
        while n < 3:
            try:
                url = "https://tmi.twitch.tv/group/user/" + self.channel \
                    + "/chatters"
                resp = requests.get(url=url)
                data = json.loads(resp.content)
                all_users = []
                for user_type in data['chatters']:
                    [all_users.append(str(user)) for user in data[
                        "chatters"][user_type]]
                return data, all_users # in the same format as dummy
            except ValueError:  # "No JSON object could be decoded"
                n += 1  # make sure n increases value by one on each loop
                if n < 3:  # if it's not, it will exit the loop
                    continue  # go back to the beginning of the loop
            except:  # in case of an unexpected error
                return dummy, []
        return dummy, []  # will only happen after three ValueErrors in a row

    def follower_status(self):
        url = "https://api.twitch.tv/kraken/users/" + self.user \
            + "/follows/channels/" + self.channel
        resp = requests.get(url=url)
        data = json.loads(resp.content)
        return data

    def stream(self):
        url = "https://api.twitch.tv/kraken/streams/" + \
            self.channel
        resp = requests.get(url=url)
        data = json.loads(resp.content)
        return data

    def followers(self, limit=5):
        url = "https://api.twitch.tv/kraken/channels/" + \
            self.channel + "/follows?limit=" + str(limit)
        resp = requests.get(url=url)
        data = json.loads(resp.content)
        return data

    def game(self, game, limit=5):
        game = game.replace(" ", "%20")
        url = "https://api.twitch.tv/kraken/search/streams?q=" + \
            game + "&limit=" + str(limit)
        resp = requests.get(url=url)
        data = json.loads(resp.content)
        return data

    def highlight(self, limit=5):
        url = "https://api.twitch.tv/kraken/channels/" + \
            self.channel + "/videos?limit=" + str(limit)
        resp = requests.get(url=url)
        data = json.loads(resp.content)
        return data


if __name__ == "__main__":
    # This allows us to use a plain HTTP callback
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app = Flask(__name__)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    os.environ['DEBUG'] = "1"
    app.secret_key = os.urandom(24)

    @app.route("/twitch/authorize")
    def twitch_authorize():
        """Step 1: User Authorization.

        Redirect the user/resource owner to the OAuth provider (i.e. Github)
        using an URL with a few key OAuth parameters.
        """
        authorization_base_url = "https://api.twitch.tv/kraken/oauth2/authorize" + \
            "?response_type=code" + \
            "&client_id=" + twitch_client_id + \
            "&redirect_uri=" + twitch_redirect_uri
        scope = twitch_scopes
        twitch = OAuth2Session(
            client_id=twitch_client_id, scope=scope,
            redirect_uri=twitch_redirect_uri)
        authorization_url, state = twitch.authorization_url(
            authorization_base_url)
        # State is used to prevent CSRF, keep this for later.
        session['oauth_state'] = state
        return redirect(authorization_url)

    @app.route("/twitch/authorized", methods=["GET", "POST"])
    def twitch_authorized():
        """ Step 3: Retrieving an access token.

        The user has been redirected back from the provider to your registered
        callback URL. With this redirection comes an authorization code included
        in the redirect URL. We will use that to obtain an access token.
        """
        token_url = "https://api.twitch.tv/kraken/oauth2/token"
        code = request.args.get('code', '')
        twitch = OAuth2Session(
            client_id=twitch_client_id, scope=twitch_scopes,
            redirect_uri=twitch_redirect_uri)
        token = twitch.fetch_token(
            token_url, client_secret=twitch_client_secret, code=code)
        username_url = "https://api.twitch.tv/kraken?oauth_token=" + \
            token["access_token"]
        username_resp = requests.get(url=username_url)
        username = json.loads(username_resp.content)["token"]["user_name"]
        con = lite.connect("twitch.db", check_same_thread=False)
        with con:
            cur = con.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS auth(
                    id INTEGER PRIMARY KEY,
                    channel TEXT UNIQUE, twitch_oauth TEXT,
                    twitchalerts_oauth TEXT, streamtip_oauth TEXT);
            """)
            con.commit()
            cur.execute("""
                INSERT OR IGNORE INTO auth VALUES (NULL, ?, ?, NULL, NULL);
            """, [username, token["access_token"]])
            cur.execute("""
                UPDATE auth SET twitch_oauth = ? WHERE channel = ?;
            """, [token["access_token"], username])
        return str("It worked! Thanks, " + username)
