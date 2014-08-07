#!/opt/local/python3.3

#http://tweepy.github.com/examples/basic_auth.html
import tweepy

username = ""
password = ""

auth = tweepy.auth.BasicAuthHandler(username, password)

api = tweepy.API(auth)

api.update_status('Dinklebottom mcfluffinpants!')
