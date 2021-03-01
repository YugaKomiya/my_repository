# -*- coding: utf-8 -*-
from __future__ import print_function
from dics import members, color_dic
from PIL import Image, ImageDraw
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from os.path import join, dirname
import os
import unicodedata
import gspread
import json
import re
import tweepy
import urllib.request
import urllib.error
import time

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# drive_folder_ID
folder_id = os.environ['GOOGLE_DRIVE_DIR_ID']

sl_time = 3


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
    # 認証部分
    # 2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
    """
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    """
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive',
             'https://www.googleapis.com/auth/drive.file',
             'https://www.googleapis.com/auth/drive.install']

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
    # spreadsheet用
    gc = gspread.authorize(credentials)

    # 共有設定したスプレッドシートキーを変数[SPREADSHEET_KEY]に格納する。
    SPREADSHEET_KEY = os.environ['SPREADSHEET_KEY']

    # 共有設定したスプレッドシートのシート1を開く
    worksheet = gc.open_by_key(SPREADSHEET_KEY).sheet1

    # pydrive用にOAuth認証を行う
    gauth = GoogleAuth()
    gauth.credentials = credentials
    drive = GoogleDrive(gauth)

    # sheet と drive 認証情報を返す
    return worksheet, drive


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


# drive に アイコン、ヘッダーを上げる
# drive からダウンロードする
def drive_img_up_down_load(drive, contents, members):
    drive_icon_img = '{}_icon_{}.png'
    drive_header_img = '{}_header_{}.png'

    folder_len = drive.ListFile(
        {'q': '"{}" in parents'.format(folder_id)}).GetList()

    # len(folder_len) == 0 が true なら drive にアップ
    if len(folder_len) == 0:
        for name in members:
            icon_name = drive_icon_img.format('old', name)
            header_name = drive_header_img.format('old', name)

            icon_img_2 = drive.CreateFile(
                {'parents': [{'kind': 'drive#fileLink', 'id': folder_id}]})
            icon_img_2.SetContentFile(icon_name)
            icon_img_2.Upload()
            # icon_ids.append(icon_img_2['id'])

            header_img_2 = drive.CreateFile(
                {'parents': [{'kind': 'drive#fileLink', 'id': folder_id}]})
            header_img_2.SetContentFile(header_name)
            header_img_2.Upload()
            # header_ids.append(header_img_2['id'])
    else:
        # len(folder_len) == 0 が falth なら drive からダウンロード
        for f in folder_len:
            #f.GetContentFile(os.path.join('file', f['title']))
            f.GetContentFile(f['title'])


# 変更された画像をアップロード
def drive_img_update(drive, contents, members, update_img):
    # 最新版を更新
    folder_len = drive.ListFile(
        {'q': '"{}" in parents'.format(folder_id)}).GetList()

    for f in folder_len:
        if f['title'] == update_img:
            f_id = f['id']

    file_ud = drive.CreateFile({'title': update_img,
                                # 'mimeType': 'image/png',
                                'parents': [{'kind': 'drive#fileLink', 'id': folder_id}],
                                'id': f_id})
    file_ud.SetContentFile(update_img)
    file_ud.Upload()


# urlにある画像をdst_pathで指定したパスにダウンロードする
def download_image(url, dst_path):
    try:
        data = urllib.request.urlopen(url).read()
        with open(dst_path, mode="wb") as f:
            f.write(data)
    except urllib.error.URLError as e:
        print(download_error_img)


# 画像と一緒にツイートする
# tweetはツイートする文章、filesは画像のパスのlist
def tweet_with_imgs(tweet, img):
    api = twitter_api()
    time.sleep(sl_time)
    api.update_with_media(filename=img, status=tweet)


# 2つの画像をつなげた画像を作る
# im1_path, im2_pathでパスを指定した2画像を矢印でつなげ、gen_img_nameというパスに保存
# アイコン用
def concatenate_icon(im1_path, im2_path, gen_img_name, name):
    im1 = Image.open(im1_path)
    im2 = Image.open(im2_path)

    void_pix = 30
    dst_width = im1.width + im2.width + void_pix
    dst_height = max(im1.height, im2.height)
    dst = Image.new('RGBA', (dst_width, dst_height), (128, 128, 128))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width + void_pix, 0))

    draw = ImageDraw.Draw(dst)
    line_xm = int(im1.width - 15)
    line_xp = int(dst_width - im2.width + 10)
    line_y = int(dst_height / 2)
    line_width = 30
    arrow_x = line_xp - 5
    line_coor = (line_xm, line_y, line_xp, line_y)
    arrow_coor = (line_xp+line_width/2, line_y,
                  arrow_x, line_y+line_width,
                  arrow_x, line_y-line_width)

    line_c = (color_dic[name][0], color_dic[name][1], color_dic[name][2])

    draw.line(line_coor, fill=line_c, width=line_width)
    draw.polygon(arrow_coor, fill=line_c)
    dst.save(gen_img_name)


# 2つの画像をつなげた画像を作る
# ヘッダー用 アイコン用とやってることは同じ
def concatenate_header(im1_path, im2_path, gen_img_name, name):
    im1 = Image.open(im1_path)
    im2 = Image.open(im2_path)

    void_pix = 30
    dst_width = max(im1.width, im2.width)
    dst_height = im1.height + im2.height + void_pix
    dst = Image.new('RGBA', (dst_width, dst_height), (128, 128, 128))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height + void_pix))

    # ImageDrawオブジェクトの生成
    draw = ImageDraw.Draw(dst)
    line_x = int(im1.width / 2)
    line_ym = int(im1.height - 20)
    line_yp = int(dst_height - im2.height + 15)

    line_width = 40
    arrow_y = line_yp - 10

    line_coor = (line_x, line_ym, line_x, line_yp)

    # 三角形の描画
    # 3つの頂点の座標
    arrow_coor = (line_x + line_width, arrow_y,
                  line_x - line_width, arrow_y,
                  line_x, line_yp + line_width/2)

    line_c = (color_dic[name][0], color_dic[name][1], color_dic[name][2])

    draw.line(line_coor, fill=line_c, width=line_width)
    draw.polygon(arrow_coor, fill=line_c)
    dst.save(gen_img_name)
