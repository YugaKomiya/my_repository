# -*- coding: utf-8 -*-
from __future__ import print_function
from dics import tw_url_dic, tw_id_dic
from os.path import join, dirname
from dotenv import load_dotenv
from tools import twitter_api
import os
import time
#import requests
import json

api = twitter_api()
sl_time = 3


# Twitterプロフィールの内容を返す。
# tw_icon、tw_bannerは画像のURLが入っている。
def get_twitter_profile(name):
    time.sleep(sl_time)

    id = tw_id_dic[name]
    tw_user = api.get_user(id)
    tw_name = tw_user.name
    tw_desc = tw_user.description.replace('\n', ' ')
    tw_place = tw_user.location
    tw_url = tw_user.url
    tw_icon = tw_user.profile_image_url.replace('normal', '400x400')
    tw_banner = tw_user.profile_banner_url

    contents = {
        '名前': tw_name,
        'bio': tw_desc,
        '場所': tw_place,
        'URL': tw_url,
        'アイコン': tw_icon,
        'ヘッダー': tw_banner
    }

    return contents
