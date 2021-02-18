# -*- coding: utf-8 -*-
from __future__ import print_function
import os
from os.path import join, dirname
import unicodedata
import re
import tweepy
from dotenv import load_dotenv

# Twitterでツイートしたりデータを取得したりする準備


def twitter_api():
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    CONSUMER_KEY = os.environ['API_KEY']
    CONSUMER_SECRET = os.environ['API_SECRET_KEY']
    ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
    ACCESS_SECRET = os.environ['ACCESS_TOKEN_SECRET']

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)

    return api
