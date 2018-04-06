import config

import tweepy
import os
import datetime

date = datetime.datetime.now().date().strftime('%d %B %Y')

os.system("gnuplot -e \"date=\'{}\';\" plot.gnuplot".format(date))

plotpath = "counts.png"

auth = tweepy.OAuthHandler(config.consumer_key,config.consumer_secret)
auth.set_access_token(config.access_token,config.access_secret)
api = tweepy.API(auth)

api.update_with_media(plotpath,status="@{} Egg Tally: {}".format(config.twitter_user,date))

os.system("rm counts.dat counts.png")
