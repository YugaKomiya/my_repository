# -*- coding: utf-8 -*-
# channel_report チャンネル名 登録者数 動画数 開設日
# videos_report 動画id 動画タイトル 再生数 高評価数 低評価数 コメント数 投稿(配信)日
# 今日の日付でcsv保存
# 保存したcsvを読み込みDBにインする
# 既にDBに入ってるものを昨日の日付でcsv出力
# csvをドライブに投げる

from drive_upload_csv import upload_csv
from db_access import db_connect
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from os.path import join, dirname
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine
import datetime
import os
import pandas as pd
#import psycopg2

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

API_KEY = os.environ['YOUTUBE_API_KEY']
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
CHANNEL_ID = os.environ['CHANNEL_ID']
channels = [] # チャンネル情報を格納する配列
searches = [] # videoidを格納する配列
videos = [] # 各動画情報を格納する配列
st = datetime.datetime(2019, 6, 1).isoformat()+'Z'  # search開始年月日 本番 2019, 6, 1
ed = datetime.datetime.today().isoformat()+'Z'
to_day = datetime.date.today() # 今日 20XX-YY-ZZ
today_file_path = f'./{to_day}.csv' # './20XX-YY-ZZ.csv'
yester_day = datetime.date.today() - relativedelta(days=1)
yesterday_yv_file_path = f"./youtubevideos_{yester_day}.csv" # './20XX-YY-(ZZ-1).csv'
yesterday_sl_file_path = f"./songlist_{yester_day}.csv" # './20XX-YY-(ZZ-1).csv'

# DB接続エンジンを作成
DATABASE_URL = os.environ['DATABASE_URL_2'] # DATABASE_URL
engine = create_engine(DATABASE_URL)

# DB接続
con = db_connect()


# DBからcsvを出力(youtube_videos)
def youtubevideos_output():
	with con.cursor() as cur:
		cur.execute('select * from youtube_videos;')
		rows = cur.fetchall()
		con.commit()
	try:
		yesterday_report = pd.DataFrame(rows, columns=['id', 'title', 'viewcount', 'likecount', 'dislikecount', 'commentcount', 'publishedat'])
		yesterday_report.to_csv(yesterday_yv_file_path, index=None, encoding='utf-8')
		print('yv output ok!')
	except:
		print('yv output error')


# DBからcsvを出力(song_list)
def songlist_output():
	with con.cursor() as cur:
		cur.execute('select * from song_list;')
		rows = cur.fetchall()
		con.commit()
	try:
		song_list_items = pd.DataFrame(rows, columns=['id','song_title', 'song_url', 'initial', 'artist_anime_name', 'vocaloid', 'sound_source', 'day', 'pf', 'stream_title', 'stream_url', 'created_at'])
		song_list_items.to_csv(yesterday_sl_file_path, index=None, encoding='utf-8')
		print('sl output ok!')
	except:
		print('sl output error')


# youtubeを叩く
def get_youtube_data():
	nextPagetoken = None
	nextpagetoken = None

	youtube = build(
		YOUTUBE_API_SERVICE_NAME, 
		YOUTUBE_API_VERSION,
		developerKey=API_KEY
	)

	channel_response = youtube.channels().list(
		part = 'snippet,statistics',
		id = CHANNEL_ID
	).execute()

	for channel_result in channel_response.get("items", []):
		if channel_result["kind"] == "youtube#channel":
			channels.append([channel_result["snippet"]["title"],channel_result["statistics"]["subscriberCount"],channel_result["statistics"]["videoCount"],channel_result["snippet"]["publishedAt"]])

	while True:
		if nextPagetoken != None:
			nextpagetoken = nextPagetoken

		search_response = youtube.search().list(
			part = "snippet",
			channelId = CHANNEL_ID,
			maxResults = 50,
			order = "date", #日付順にソート
			publishedAfter=st,  # '2019-06-01T00:00:00Z',
			publishedBefore=ed,  # '今日',
			pageToken = nextpagetoken #再帰的に指定
		).execute()

		for search_result in search_response.get("items", []):
			if search_result["id"]["kind"] == "youtube#video":
				searches.append(search_result["id"]["videoId"])

		try:
			nextPagetoken =  search_response["nextPageToken"]
		except:
			break

	for result in searches:
		video_response = youtube.videos().list(
			part = 'snippet, statistics',
			id = result
		).execute()

		for video_result in video_response.get("items", []):
			# pprint.pprint(video_result)
			if video_result["kind"] == "youtube#video":
				videos.append([video_result["id"],video_result["snippet"]["title"],video_result["statistics"]["viewCount"],video_result["statistics"]["likeCount"],video_result["statistics"]["dislikeCount"],video_result["statistics"]["commentCount"],video_result["snippet"]["publishedAt"]])  

	csv_file = f"{to_day}.csv"
	try:
		videos_report = pd.DataFrame(videos, columns=['id', 'title', 'viewcount', 'likecount', 'dislikecount', 'commentcount', 'publishedat'])
		videos_report.to_csv(csv_file, index=None, encoding='utf-8')
		channel_report = pd.DataFrame(channels, columns=['title', 'subscribercount', 'videocount', 'publishedat'])
		channel_report.to_csv("channels_report.csv", index=None)

		print('report_videos ok!')
	except:
		print('error')


# csvから読み取って格納
def insert_yt_data():
	#today_file_path = f'./{to_day}.csv' # './20XX-YY-ZZ.csv'
	csv_file = pd.read_csv(today_file_path, encoding='utf-8')
	
	try:
		with con.cursor() as cur:
			cur.execute('drop table youtube_videos;')
			con.commit()
		print('drop ok!')
	except:
		print('drop error')

	try:
		with con.cursor() as cur:
				cur.execute('create table youtube_videos(id text, title text, viewcount integer, likecount integer, dislikecount integer, commentcount integer, publishedat date);')
				con.commit()
		print('create youtube_videos ok!')
	except:
		print('create youtube_videos error')

	try:
		csv_file.to_sql('youtube_videos', con=engine, if_exists='append', index=False)
		print('copy ok!')
	except:
		print('copy error')

	sql='select * from youtube_videos;'
	select_result = pd.read_sql(sql, con=engine)
	#print(select_result)


if __name__ == "__main__":
	youtubevideos_output()
	songlist_output()
	upload_csv()
	get_youtube_data()
	insert_yt_data()