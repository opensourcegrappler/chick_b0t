#todo: tidy up this script


import tweepy
import wget
import pathlib

#import api keys
import config

auth = tweepy.OAuthHandler(config.consumer_key,config.consumer_secret)
auth.set_access_token(config.access_token,config.access_secret)

api = tweepy.API(auth)

tweets = api.user_timeline(screen_name=config.twitter_user,
                           count=200, include_rts=False,
                           exclude_replies=True)

last_id = tweets[-1].id

while(True):
    more_tweets = api.user_timeline(screen_name=config.twitter_user,
                           count=200, include_rts=False,
                                    exclude_replies=True,
                                    max_id=last_id-1)
    if(len(more_tweets)==0):
        break
    else:
        last_id = more_tweets[-1].id-1
        tweets=tweets+more_tweets

media_files = set()
for status in tweets:
    media = status.entities.get('media',[])
    if ("EggCheck_image_" in status.text) and (len(media)>0):
        media_files.add(media[0]['media_url'])

datadir = "DATASET_object/images"
new_image = False

count=0

for media_file in media_files:
    filename = pathlib.PurePath(datadir,media_file.split('/')[-1])
    if pathlib.Path(filename).is_file():
        new_image=True

    if new_image==False:
        print count,"  found a new image",media_file
        wget.download(media_file,out=datadir)
        count+=1
    else:
        print "got this one already"
        
    #reset
    new_image=False

