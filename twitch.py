import requests
import json
from settings import client_id, client_secret, redirect_uri, scopes, token


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
                return data  # in the same format as dummy
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

    def authenticate(
            self, client_id=client_id, client_secret=client_secret,
            redirect_uri=redirect_uri, scopes=scoped, token=token):
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
