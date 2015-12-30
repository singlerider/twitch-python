import requests
import json


class Twitch:

    def __init__(self, channel, user):
        self.channel = channel
        self.user = user

    def users(self):
        n = 0
        # this endpoint fails often
        while n < 3:
            dummy = {
                "_links": {}, "chatters_count": 0, "chatters": {
                    "staff": [], "admin": [], "global_mods": [],
                    "viewers": [], "moderators": []}}
            try:
                url = "https://tmi.twitch.tv/group/user/" + self.channel \
                    + "/chatters"
                resp = requests.get(url=url)
                data = json.loads(resp.content)
                return data
            except ValueError:
                n += 1
                if n < 3:
                    continue
            except:
                return dummy
        return dummy

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

    def authenticate(self, client_id, client_secret, redirect_uri, scopes, token):
        # scopes are space separated
        user_url = "https://api.twitch.tv/kraken/oauth2/authorize" + \
            "?response_type=code" + \
            "&client_id=" + client_id + \
            "&redirect_uri=" + redirect_uri + \
            "&scope=" + scopes + \
            "&state=" + token
        # URL-encoded POST
        uri_url = "https://" + redirect_uri + "/?code=" + code
        post_url = "https://api.twitch.tv/kraken/oauth2/token" + \
            "client_id=" + client_id + \
            "&client_secret=" + client_secret + \
            "&grant_type=authorization_code" + \
            "&redirect_uri=" + \
            "&code=" + code + \
            "&state=" + token
