# -*- coding: utf-8 -*-
from __future__ import print_function
from dics import members
import os
from os.path import join, dirname
import unicodedata
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import json
import re
import tweepy
import urllib.request
import urllib.error
from PIL import Image, ImageDraw
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


# Twitterでツイートしたりデータを取得したりする準備
def twitter_api():

    CONSUMER_KEY = os.environ['API_KEY']
    CONSUMER_SECRET = os.environ['API_SECRET_KEY']
    ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
    ACCESS_SECRET = os.environ['ACCESS_TOKEN_SECRET']

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)

    return api


# GCP認証
def google_api():
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


# cell_dict(main) が空の場合、取ったデータを書き出す
def update_sheet(contents, worksheet):
    cell_dict = []
    for row, name in enumerate(members):
        col = 1
        for key in contents[name].keys():
            worksheet.update_cell(row+2, col, contents[name][key])
            col += 1
    # sheetから取り出す
    cell_dict = worksheet.get_all_records(
        empty2zero=False, head=1, default_blank='')

    return cell_dict


# urlにある画像をdst_pathで指定したパスにダウンロードする
def download_image(url, dst_path):
    try:
        data = urllib.request.urlopen(url).read()
        with open(dst_path, mode="wb") as f:
            f.write(data)
    except urllib.error.URLError as e:
        print(e)


# 画像と一緒にツイートする
# tweetはツイートする文章、filesは画像のパスのlist
def tweet_with_imgs(tweet, files):
    api = twitter_api()

    # media_idsは投稿したい画像のidを入れるためのリスト
    media_ids = []

    for i in range(len(files)):
        img = api.media_upload(files[i])
        media_ids.append(img.media_id_string)

    time.sleep(sl_time)
    api.update_status(status=tweet, media_ids=media_ids)


# 2つの画像をつなげた画像を作る
# im1_path, im2_pathでパスを指定した2画像を矢印でつなげ、gen_img_nameというパスに保存
def concatenate_icon(im1_path, im2_path, gen_img_name):
    im1 = Image.open(im1_path)
    im2 = Image.open(im2_path)

    void_pix = 30
    dst_width = im1.width + im2.width + void_pix
    dst_height = max(im1.height, im2.height)
    dst = Image.new('RGBA', (dst_width, dst_height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width + void_pix, 0))

    draw = ImageDraw.Draw(dst)
    line_xm = int(im1.width - 5)
    line_xp = int(dst_width - im2.width - 5)
    line_y = int(dst_height / 2)
    line_width = 20
    arrow_x = line_xp - 5
    line_coor = (line_xm, line_y, line_xp, line_y)
    arrow_coor = (line_xp+line_width/2, line_y,
                  arrow_x, line_y+line_width,
                  arrow_x, line_y-line_width)
    line_c = (70, 170, 255)
    draw.line(line_coor, fill=line_c, width=line_width)
    draw.polygon(arrow_coor, fill=line_c)
    dst.save(gen_img_name)
