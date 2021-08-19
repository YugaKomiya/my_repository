# -*- coding: utf-8 -*-
# スプレッドシートから拾ってくる
from oauth2client.service_account import ServiceAccountCredentials
from os.path import join, dirname
from dotenv import load_dotenv
import json
import os
import gspread
import pprint

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# GCP認証
# 2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

# 辞書オブジェクト。認証に必要な情報をHerokuの環境変数から呼び出している

credential = {
    "type": "service_account",
    "project_id": os.environ['SHEET_PROJECT_ID'],
    "private_key_id": os.environ['SHEET_PRIVATE_KEY_ID'],
    "private_key": os.environ['SHEET_PRIVATE_KEY'].replace('\\n', '\n').encode('utf-8'),
    "client_email": os.environ['SHEET_CLIENT_EMAIL'],
    "client_id": os.environ['SHEET_CLIENT_ID'],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.environ['SHEET_CLIENT_X509_CERT_URL']
}

# print(credential['private_key'])

# 認証情報設定
# ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    credential, scope)

# print(credential['private_key'])

# 認証情報設定
# ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    credential, scope)

# print(credentials)

# 環境変数の中身をjsonにパースしてから利用する
# secret = os.environ['GCP_SS_KEY']
# oath_obj = InstalledAppFlow.from_client_config(secret, scope)

# OAuth2の資格情報を使用してGoogle APIにログインします。
gc = gspread.authorize(credentials)

# 共有設定したスプレッドシートキーを変数[SPREADSHEET_KEY]に格納する。
SPREADSHEET_KEY = os.environ['SPREADSHEET_KEY']

# 共有設定したスプレッドシートのシート1を開く
worksheet = gc.open_by_key(SPREADSHEET_KEY).sheet1

sheet_data = []
sheet_data = worksheet.get_all_records(
    empty2zero=False, head=1, default_blank='')

# pprint.pprint(sheet_data[0])

json_file = open('videolist.json', 'r')
json_load = json.load(json_file)
# pprint.pprint(json_load)

# sheet と json からとったデータが一致しているかチェック
list_sheet = []
list_json = []
list_title = []
for sheet_data_i in sheet_data:
    # print(sheet_data_i['配信タイトル'])
    list_sheet.append(sheet_data_i['配信タイトル'])

    for json_load_n in json_load:
        # print(json_load_n['title'])
        list_json.append(json_load_n['title'])

        if sheet_data_i['配信タイトル'] == json_load_n['title']:
            # print(sheet_data_i['配信タイトル'])
            list_title.append(sheet_data_i['配信タイトル'])

nums_unique01 = list(set(list_sheet))
print(len(nums_unique01))

nums_unique02 = list(set(list_json))
print(len(nums_unique02))

nums_unique03 = list(set(list_title))
pprint.pprint(nums_unique03)
# print(len(nums_unique03))

""""
contents = {
    '曲名': sheet_data[0]['曲名'],
    '該当URL': sheet_data[0]['該当URL'],
    '検索用頭文字': sheet_data[0]['検索用頭文字'],
    'アーティスト名アニメ名': sheet_data[0]['アーティスト名_アニメ名'],
    'VOCALOID': sheet_data[0]['VOCALOID'],
    '音源': sheet_data[0]['音源'],
    '放送日': sheet_data[0]['放送日'],
    '配信PF': sheet_data[0]['配信PF'],
    '配信タイトル': sheet_data[0]['配信タイトル'],
    '配信URL': sheet_data[0]['配信URL']
}
# print(contents)
"""

"""
# A1セルの値を受け取る
import_value = str(worksheet.acell('A1').value)
print(import_value)
"""
