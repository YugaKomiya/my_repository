# -*- coding: utf-8 -*-
# DBにアクセスする

from linebot.models import *
from linebot.exceptions import (
	InvalidSignatureError, LineBotApiError
)
from linebot import (
	LineBotApi, WebhookHandler
)
from os.path import join, dirname
from dotenv import load_dotenv
import os
import psycopg2

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# 環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ['YOUR_CHANNEL_ACCESS_TOKEN']
YOUR_CHANNEL_SECRET = os.environ['YOUR_CHANNEL_SECRET']

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


# DB接続
def db_connect():
	try:
		HOST = os.environ['HOST']
		PORT_DB = os.environ['PORT_DB']
		DB_NAME = os.environ['DB_NAME']
		USER = os.environ['USER']
		PASSWORD = os.environ['PASSWORD']

		con = psycopg2.connect('host=' + HOST +
							   ' port=' + PORT_DB +
							   ' dbname=' + DB_NAME +
							   ' user=' + USER +
							   ' password=' + PASSWORD)

		return con
	except Exception as e:
		print(e)
		print('db_connect_error')


# select文実行
def select_execute(con, sql):
	with con.cursor() as cur:
		cur.execute(sql)
		rows = cur.fetchall()
		con.commit()

	return rows


# user_sate にいれる
def insert_state(con, USER_ID, state):
	state = int(state)
	sql = f"insert into user_state values('{USER_ID}', {state});"

	with con.cursor() as cur:
		cur.execute(sql)
		con.commit()


def update_state(con, USER_ID, state):
	state = int(state)
	sql = f"update user_state set state = {state} where user_id = '{USER_ID}';"

	with con.cursor() as cur:
		cur.execute(sql)
		con.commit()


# user_sate id検索
def id_search(con, USER_ID, state):
	sql = f"select state from user_state where user_id = '{USER_ID}';"
	with con.cursor() as cur:
		cur.execute(sql)
		row = cur.fetchone()
		con.commit()

	if row == None:
		insert_state(con, USER_ID, state)
		id_search(con, USER_ID, state)
	else:
		#print(row[0])
		return row[0]
		

# idを削除
def id_delete(con, USER_ID):
	sql = f"delete from user_state where user_id = '{USER_ID}';"
	try:
		with con.cursor() as cur:
			cur.execute(sql)
			con.commit()
		return True
	except Exception:
		return False