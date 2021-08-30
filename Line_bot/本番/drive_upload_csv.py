# -*- coding: utf-8 -*-

from oauth2client.service_account import ServiceAccountCredentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from os.path import join, dirname
from dotenv import load_dotenv
from dateutil.relativedelta import relativedelta
import datetime
import os

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

folder_id = os.environ['GOOGLE_DRIVE_DIR_ID'] # googledrive フォルダのID
yester_day = datetime.date.today() - relativedelta(days=1)
yesterday_yv_file_path = f"youtubevideos_{yester_day}.csv" # '20XX-YY-(ZZ-1).csv'

yesterday_sl_file_path = f"songlist_{yester_day}.csv" # '20XX-YY-(ZZ-1).csv'


# google driveの認証
def google_api():
	scope = ['https://www.googleapis.com/auth/drive.file']

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

	# pydrive用にOAuth認証を行う
	gauth = GoogleAuth()
	gauth.credentials = credentials
	drive = GoogleDrive(gauth)

	# drive 認証情報を返す
	return drive


def upload_csv():
	drive = google_api()

	# youtube_videos の中身を投げる
	try:
		f = drive.CreateFile({'title': yesterday_yv_file_path,
							'mimeType': 'text/csv',
							'parents': [{"id": folder_id}]}
							)
		f.SetContentFile(yesterday_yv_file_path)
		f.Upload()
		print('yv drive upload ok!')

	except Exception:
		print('yv drive upload error')


	# song_list　の中身を投げる
	try:
		f = drive.CreateFile({'title': yesterday_sl_file_path,
							'mimeType': 'text/csv',
							'parents': [{"id": folder_id}]}
							)
		f.SetContentFile(yesterday_sl_file_path)
		f.Upload()
		print('sl drive upload ok!')

	except Exception:
		print('sl drive upload error')