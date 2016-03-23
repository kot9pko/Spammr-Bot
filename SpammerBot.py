#/usr/bin/python2

import tweepy
import telebot
import requests
import re
from config import *

telegram = telebot.TeleBot(tgToken)
auth = tweepy.OAuthHandler(twConsumerKey, twConsumerSecret)
auth.secure = True
auth.set_access_token(twAccessToken, twAccessTokenSecret)
twitter = tweepy.API(auth)
registeredUser = True


# SCRIPT
def listener(messages):
    global registeredUser
    for message in messages:
        tgContact = message.from_user.username
        tgChatID = message.chat.id
        print tgChatID
        if message.content_type == "text":
            if message.text.startswith("/"):
                if tgContact in tgUsernames:
                    text = message.text
                    print tgContact + ": " + text
                    registeredUser = True
                    print "Registered user"
                else:
                    registeredUser = False
                    telegram.send_message(tgChatID, "Sorry, you are not allowed to use this bot")
                    print "Unregistered user, access denied"
                    return
            
        elif message.content_type == 'photo':
            print "Photo here"
            if tgContact in tgUsernames:
                caption = None
                try:
                    caption = message.caption
                except Exception:
                    print "No photo caption here"
                    return
                if caption.startswith("/tweet"):
                    caption = caption.replace("/tweet", "")
                    tweet_photo(message, caption)
                    telegram.send_message(tgChatID, "Photo twitted successfully")

@telegram.message_handler(content_types=['photo'])
def tweet_photo(message, status):
    file_id = message.photo[1].file_id
    path = telegram.get_file_obj(file_id)['file_path']
    print path
    telegram._get_file(path, path)
    twitter.update_with_media(path, status=status)

@telegram.message_handler(commands=['tweet'])
def command_tweet(tweet):
    global registeredUser
    tgChatID = tweet.chat.id
    twText = tweet.text
    twText = twText.replace("/tweet ", "")
    if registeredUser:
        if len(twText) <= 140 and registeredUser:
            img = url_to_image(twText)
            if img:
                twitter.update_with_media(img, status=twText)
                print "Image from URL attached"
            else:
                twitter.update_status(status=twText)
            telegram.send_message(tgChatID, "Tweet successful")
            print "Tweet successful"
        else:
            telegram.send_message(tgChatID, "Sorry, wrong Twitter API Keys or message too long (max: 140 char.)")
            print "Sorry, wrong Twitter API Keys or message too long (max: 140 char.)"

def url_to_image(text):
    url_re = re.search(r'((\w+):\/\/)?([^ ]+)\.(\w+)\/([^ ]+)', text)
    try:
        url = url_re.group(0)
    except AttributeError:
        return False
    r = requests.get(url, stream=True)
    print r.headers['content-type']
    image_type = r.headers['content-type'].split("/")[1]
    file_name = 'url_to_image.%s' % image_type
    if r.status_code == 200 and r.headers['content-type'].startswith("image"):
        with open(file_name, 'wb') as f:
            for chunk in r:
                f.write(chunk)
        return file_name
    else:
        return False

telegram.set_update_listener(listener)
telegram.polling()
telegram.polling(none_stop=True)
telegram.polling(interval=1)


while True:
    pass
