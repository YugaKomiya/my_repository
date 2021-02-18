# -*- coding: utf-8 -*-
from __future__ import print_function
from dics import tw_url_dic, tw_id_dic
import os
from os.path import join, dirname
import time
import requests
import json
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
import gspread

from tools import twitter_api
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
    #tw_place    = tw_user.location
    tw_url = tw_user.url
    #tw_icon     = tw_user.profile_image_url.replace('normal', '400x400')
    #tw_banner   = tw_user.profile_banner_url

    contents = {
        '名前': tw_name,
        '概要欄': tw_desc,
        # '場所' : tw_place, \
        'URL': tw_url
        # 'アイコン' : tw_icon, \
        # 'バナー' : tw_banner
    }

    return contents


def get_sheet_data():
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    # 認証部分
    # 2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    # 辞書オブジェクト。認証に必要な情報をHerokuの環境変数から呼び出している
    credential = {
        'type': 'service_account',
        'project_id': os.environ['SHEET_PROJECT_ID'],
        'private_key_id': os.environ['SHEET_PRIVATE_KEY_ID'],
        'private_key': os.environ['SHEET_PRIVATE_KEY'].replace('\\n', '\n').encode('utf-8'),
        'client_email': os.environ['SHEET_CLIENT_EMAIL'],
        'client_id': os.environ['SHEET_CLIENT_ID'],
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
        'client_x509_cert_url': os.environ['SHEET_CLIENT_X509_CERT_URL']
    }

    # 認証情報設定
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        credential, scope)

    # OAuth2の資格情報を使用してGoogle APIにログインします。
    gc = gspread.authorize(credentials)

    # 共有設定したスプレッドシートキーを変数[SPREADSHEET_KEY]に格納する。
    SPREADSHEET_KEY = os.environ['SPREADSHEET_KEY']

    # 共有設定したスプレッドシートのシート1を開く
    worksheet = gc.open_by_key(SPREADSHEET_KEY).sheet1

    return worksheet
