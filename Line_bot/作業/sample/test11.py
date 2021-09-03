# -*- coding: utf-8 -*-
# お歌リストとyoutubeのデータを照合
# お歌リストに動画IDを追加したい

from db_access import db_connect
from os.path import join, dirname
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd
import pprint
import psycopg2
import os

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# DB接続エンジンを作成
DATABASE_URL = os.environ['DATABASE_URL']
engine = create_engine(DATABASE_URL)

# DB接続
con = db_connect()


with con.cursor() as cur:
		cur.execute("select * from song_list;")
		old_rec = cur.fetchall()


with con.cursor() as cur:
	#cur.execute("select distinct stream_title from song_list where pf='YT';")
	cur.execute("select distinct stream_title, day, stream_url from song_list where pf='YT' order by day;")
	rows_1 = cur.fetchall()
#print('******************************************************************')
#pprint.pprint(rows_1)
#print('******************************************************************')


with con.cursor() as cur:
	#cur.execute("select distinct title from youtube_videos;")
	cur.execute("select title, publishedat, id from youtube_videos order by publishedat;")
	rows_2 = cur.fetchall()
#print('=====================================================================')
#pprint.pprint(rows_2)
#print('=====================================================================')

"""
with con.cursor() as cur:
	sql = 'create table add_id_song_list (id text, song_title text, song_url text, initial text, artist_anime_name text, vocaloid text, sound_source text, day date, pf text, stream_title text, stream_url text, created_at date);'
	cur.execute(sql)
"""

with con.cursor() as cur:
	sql = "select distinct stream_title, day, stream_url from song_list where pf='YT' and song_url is NULL and stream_url is NULL order by day asc;"
	cur.execute(sql)
	nulls_title_url = cur.fetchall()
	#con.commit()


# アーカイブが消えてるやつら
# id がない
items_1 = []
for row_1 in rows_1:
	for null in nulls_title_url:
		if row_1 == null:
			#print(row_1[0])
			with con.cursor() as cur:
				sql = f"select * from song_list where stream_title = '{null[0]}' and day = '{null[1]}' order by day asc;"
				cur.execute(sql)
				rows = cur.fetchall()
				#pprint.pprint(rows[0])
			
				id_add = []
				for row in rows:
					arry = []
					arry.append(None)
					arry.extend(row)
					#print(arry)
					id_add.append(arry)
			items_1.append(id_add)

# 正解
#pprint.pprint(items[0])
print(len(items_1))

# null_id insert
for item in items_1:
	#pprint.pprint(item)
	id_null_list = pd.DataFrame(item, columns=['id', 'song_title', 'song_url', 'initial', 'artist_anime_name', 'vocaloid', 'sound_source', 'day', 'pf', 'stream_title', 'stream_url', 'created_at'])
	id_null_list.to_sql('add_id_song_list', con=engine, if_exists='append', index=False)


# 配信タイトルと配信日で 照合
items_2 = []
for row_1 in rows_1:
	for row_2 in rows_2:
		# 配信タイトルと配信日が　あってるやつ
		if row_1[0] == row_2[0] and row_1[1] == row_2[1]:
			#print(f'row_1 title: {row_1[0]} day: {row_1[1]}')
			#print(f'row_2 title: {row_2[0]} day: {row_2[1]}')

			with con.cursor() as cur:
				sql = f"select * from song_list where stream_title = '{row_1[0]}' and day = '{row_1[1]}' order by day asc;"
				cur.execute(sql)
				rows = cur.fetchall()

				id_add = []
				for row in rows:
					arry = []
					arry.append(row_2[2])
					arry.extend(row)
					#print(arry)
					id_add.append(arry)
			items_2.append(id_add)

print(len(items_2))
# 配信タイトルと配信日で id がわかるやつ 
for item in items_2:
	#pprint.pprint(item)
	id_list_1 = pd.DataFrame(item, columns=['id', 'song_title', 'song_url', 'initial', 'artist_anime_name', 'vocaloid', 'sound_source', 'day', 'pf', 'stream_title', 'stream_url', 'created_at'])
	id_list_1.to_sql('add_id_song_list', con=engine, if_exists='append', index=False)


# 配信タイトルと配信日で 照合
items_3 = []
for row_1 in rows_1:
	for row_2 in rows_2:
		# 配信タイトルと配信日が　あってるないやつ
		if row_1[0] == row_2[0] and row_1[1] != row_2[1]:
			if row_1[0] != '【生演奏ライブ🌤️❗️】#SYNCROOM 配信🌤️❗️【 #ケムリセッション 】' or row_2[0] != '【生演奏ライブ🌤️❗️】#SYNCROOM 配信🌤️❗️【 #ケムリセッション 】':
				#print(f'row_1 title: {row_1[0]} day: {row_1[1]}')
				#print(f'row_2 title: {row_2[0]} day: {row_2[1]}')

				with con.cursor() as cur:
					sql = f"select * from song_list where stream_title = '{row_1[0]}' and day = '{row_1[1]}' order by day asc;"
					cur.execute(sql)
					rows = cur.fetchall()

					id_add = []
					for row in rows:
						arry = []
						arry.append(row_2[2])
						arry.extend(row)
						#print(arry)
						id_add.append(arry)
				items_3.append(id_add)

print(len(items_3))
# 配信タイトルと配信日で id が　わからんやつ
for item in items_3:
	#pprint.pprint(item)
	id_list_2 = pd.DataFrame(item, columns=['id', 'song_title', 'song_url', 'initial', 'artist_anime_name', 'vocaloid', 'sound_source', 'day', 'pf', 'stream_title', 'stream_url', 'created_at'])
	id_list_2.to_sql('add_id_song_list', con=engine, if_exists='append', index=False)


# nico
with con.cursor() as cur:
	sql = "select * from song_list where pf = 'nico';"
	cur.execute(sql)
	nico_list = cur.fetchall()

items_4 = []
for nico in nico_list:
	arry = []
	arry.append(None)
	arry.extend(nico)
	items_4.append(arry)

print(len(items_4))

# nico を追加
id_list_3 = pd.DataFrame(items_4, columns=['id', 'song_title', 'song_url', 'initial', 'artist_anime_name', 'vocaloid', 'sound_source', 'day', 'pf', 'stream_title', 'stream_url', 'created_at'])
id_list_3.to_sql('add_id_song_list', con=engine, if_exists='append', index=False)


# TC
with con.cursor() as cur:
	sql = "select * from song_list where pf = 'TC';"
	cur.execute(sql)
	tc_list = cur.fetchall()

items_5 = []
for tc in tc_list:
	arry = []
	arry.append(None)
	arry.extend(tc)
	items_5.append(arry)

print(len(items_5))

# TC を追加
id_list_4 = pd.DataFrame(items_5, columns=['id', 'song_title', 'song_url', 'initial', 'artist_anime_name', 'vocaloid', 'sound_source', 'day', 'pf', 'stream_title', 'stream_url', 'created_at'])
id_list_4.to_sql('add_id_song_list', con=engine, if_exists='append', index=False)


# pf null
with con.cursor() as cur:
	sql = "select * from song_list where pf is NULL;"
	cur.execute(sql)
	null_pf_list = cur.fetchall()

items_6 = []
for null_pf in null_pf_list:
	arry = []
	arry.append(None)
	arry.extend(null_pf)
	items_6.append(arry)

print(len(items_6))
# pf null を追加
id_list_5 = pd.DataFrame(items_6, columns=['id', 'song_title', 'song_url', 'initial', 'artist_anime_name', 'vocaloid', 'sound_source', 'day', 'pf', 'stream_title', 'stream_url', 'created_at'])
id_list_5.to_sql('add_id_song_list', con=engine, if_exists='append', index=False)
