# -*- coding: utf-8 -*-
# csvから読み取りdataをインサートする

from logging import fatal
from linebot.models import *
from linebot.exceptions import (
	InvalidSignatureError, LineBotApiError
)
from linebot import (
	LineBotApi, WebhookHandler
)
#from db_access import db_connect
from sqlalchemy import create_engine
from os.path import join, dirname
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd
import datetime
import pprint
import csv
import os
import psycopg2

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# 環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ['YOUR_CHANNEL_ACCESS_TOKEN']
#YOUR_CHANNEL_SECRET = os.environ['YOUR_CHANNEL_SECRET']
line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)

# DB接続エンジンを作成
DATABASE_URL = os.environ['DATABASE_URL_2'] # DATABASE_URL
engine = create_engine(DATABASE_URL)

FILE_PATH = './{}.csv'


# コンテンツチェック ヘッダーに誤りがないかチェック
def cont_check(column):
	try:
		contents = {
			'id': None,
			'song_title': column['曲名'],
			'song_url': column['該当URL'],
			'initial': column['検索用頭文字'],
			'artist_anime_name': column['アーティスト名_アニメ名'],
			'vocaloid': column['VOCALOID'],
			'sound_source': column['音源'],
			'day': column['放送日'],
			'pf': column['配信PF'],
			'stream_title': column['配信タイトル'],
			'stream_url': column['配信URL'],
			'created_at': str(datetime.date.today())
		}
		# print(contents)
		return contents

	except Exception as e:
		# 入れコン終了
		print('csvのヘッダー誤り')
		print(e)
		return False


# URLからidをget
def id_check(url):
	str_1 = 'https://youtu.be/'
	str_2 = 'https://www.youtube.com/watch?v='
	result = str_1 in url
	if result == True:
		#print('https://youtu.be/')
		#print(f'{str_1} : {idx}\n')
		id = url[len(str_1):len(url)]	
		return id

	elif result == False:
		result_2 = str_2 in url
		if result_2 == True:
			#print(f'{str_2} : {idx_2}\n')
			print(url[len(str_2):len(url)])
			id = url[len(str_2):len(url)]
			return id

		else:
			print('id Noneでした')
			return None


# idを1つずつチェック
def my_db_id_check(con, id):
	try:
		with con.cursor() as cur:
			sql = f"select id from song_list where id = '{id}';"
			cur.execute(sql)
			row = cur.fetchone()
		# print(row)
		return row
	except Exception as e:
		print(e)
		return -1


# 1タイトルずつ受け取ってチェック
def my_db_title_check(con, title):
	try:
		with con.cursor() as cur:
			sql = f"select song_title stream_title from song_list where stream_title = '{title}';"
			cur.execute(sql)
			row = cur.fetchone()
	# print(row)
		return row
	except Exception as e:
		print(e)
		return -1


# mainから呼び出されてるのはこいつ
# csv から読み取ってDBにinsertする
def insert_song_data(con, event):
	csv_list = []
	file_content = []
	stream_titles = []
	urls = []
	ids = []

	message_id = event.message.id
	message_content = line_bot_api.get_message_content(message_id)
	csv_file = message_content.content

	file_path = Path(FILE_PATH.format(message_id)).absolute()

	# 書き込み
	try:
		with open(file_path, 'wb') as wf:
			wf.write(csv_file)

	except Exception:
		print('write_csv_error')
		return 'ファイルの読み込みでエラーが発生しました。'

	# ファイルを開く
	try:
		with open(file_path, 'r') as rf:
			for row in csv.DictReader(rf):
				csv_list.append(row)
	except Exception:
		print('read_csv_error')
		return 'ファイルの読み込みでエラーが発生しました。'

	# 配信タイトル, 配信URLを取得, ファイル内容をカラムに入れる
	for column in csv_list:
		result = cont_check(column)
		if not result:
			return 'ファイルの読み込みでエラーが発生しました。お手数ですがファイルの確認をお願い致します。'
		file_content.append(result)
		stream_titles.append(result['stream_title'])
		urls.append(result['stream_url'])

	# 動画idをurlから取り出す
	# youtube_videosから検索 あればidを入れる
	for n, url in enumerate(urls):
		id = id_check(url)
		if id != None:
			with con.cursor() as cur:
				sql = f"select id from youtube_videos where id = '{id}';"
				cur.execute(sql)
				row = cur.fetchone()
			if len(row) != 0:
				ids.append(id)
				print('idがありました！')
				file_content[n]['id'] = id
			else:
				print('idがありませんでした...')
				file_content[n]['id'] = id
		else:
			file_content[n]['id'] = id
	#print(file_content)

	# 一時的なtemp_tableを作成
	try:
		with con.cursor() as cur:
			sql = 'create temp table if not exists temptbl (id text, song_title text, song_url text, initial text, artist_anime_name text, vocaloid text, sound_source text, day date, pf text, stream_title text, stream_url text, created_at date) on commit preserve rows;'
			cur.execute(sql)
			#con.commit()
		print('create temptbl ok!')

	except Exception as e:
		print(e)
		print('create temptbl error!')
		return 'エラーが発生しました。すみませんが再度お試しください。'

	# csvから読み取ったものを一度temptableに入れる
	try:
		with con.cursor() as cur:
			for contents in file_content:
				sql = f"insert into temptbl values('{contents['id']}', '{contents['song_title']}', '{contents['song_url']}', '{contents['initial']}', '{contents['artist_anime_name']}', '{contents['vocaloid']}', '{contents['sound_source']}', '{contents['day']}', '{contents['pf']}', '{contents['stream_title']}', '{contents['stream_url']}', '{contents['created_at']}');"
				cur.execute(sql)
				#con.commit()
			print('temp insert ok!')

	except Exception as e:
		print(e)
		print('temp insert error')
		return 'エラーが発生しました。すみませんが再度お試しください。'

	"""
	# 確認
	with con.cursor() as cur:
		cur.execute('select * from temptbl;')
		rows = cur.fetchall()
	"""

	stream_titles = list(set(stream_titles))
	ids = list(set(ids)) # 重複idsをまとめる

	# song_list からタイトルで探す
	# なければインサートする
	record = 0
	for id in ids:
		result = my_db_id_check(con, id)

		if result == None:
			print(f'{id} : song_lsitにいれる\n')
			with con.cursor() as cur:
				cur.execute(f"select * from temptbl where id = '{id}';")
				items = cur.fetchall()
			
				insert_items = pd.DataFrame(items, columns=['id', 'song_title', 'song_url', 'initial', 'artist_anime_name', 'vocaloid', 'sound_source', 'day', 'pf', 'stream_title', 'stream_url', 'created_at'])
				insert_items.to_sql('song_list', con=engine, if_exists='append', index=False)
			
				cur.execute(f"select * from song_list where id = '{id}';")
				insert_result = cur.fetchall()
			print(insert_result)
			record = record + len(insert_result)

		elif result == -1:
			print('DBチェックで -1 を返したエラー。')
			message = 'エラーが発生しました。しばらく時間を置いて再度お試しください。error_code=-1'
			return message
		else:
			print(f'{id}: song_lsitにいれない')
			continue

	# id で見つからなかった場合
	if record == 0:
		# id が None の場合　タイトルでチェック
		print('id None で見つからなかった')

		for title in stream_titles:
			result = my_db_title_check(con, title)

			if result == None:
				print(f'stream_title  {title}:     song_lsitにいれる\n')
				with con.cursor() as cur:
					cur.execute(f"select * from temptbl where stream_title = '{title}';")
					items = cur.fetchall()
				
				insert_items = pd.DataFrame(items, columns=['id', 'song_title', 'song_url', 'initial', 'artist_anime_name', 'vocaloid', 'sound_source', 'day', 'pf', 'stream_title', 'stream_url', 'created_at'])
				insert_items.to_sql('song_list', con=engine, if_exists='append', index=False)
				
				with con.cursor() as cur:
					cur.execute(f"select * from song_list where stream_title = '{title}';")
					insert_result = cur.fetchall()
					#con.commit()

				print(insert_result)
				record = record + len(insert_result)

			elif result == -1:
				message = 'エラーが発生しました。しばらく時間を置いて再度お試しください。'
				print(message)
				return message
			else:
				print(f'{title}: song_lsitにいれない')
				continue

	# temptbl を強制的に削除
	try:
		with con.cursor() as cur:
			cur.execute('drop table temptbl;')
			con.commit()
		print('drop ok!')
	except:
		print('drop error')

	if record == 0:
		message = 'すでに登録されているようです。\nご確認いただけますと幸いです。'
		print('already_insert_title')
		return message

	elif record > 0:
		message = f'{record}件登録されました。'
		return message
