
from oauth2client.service_account import ServiceAccountCredentials
#from pydrive.auth import GoogleAuth
#from pydrive.drive import GoogleDrive
from os.path import join, dirname
from dotenv import load_dotenv
import json
import os
import gspread

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

# A1セルの値を受け取る
import_value = str(worksheet.acell('A1').value)

print(import_value)
