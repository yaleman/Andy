#!/opt/local/python3.3

import tweepy

username = ""
password = ""

auth = tweepy.auth.BasicAuthHandler(username, password)

api = tweepy.API(auth)

api.update_status('Dinklebottom mcfluffinpants!')
