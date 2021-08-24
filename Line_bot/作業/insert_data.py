# -*- coding: utf-8 -*-
from linebot.models import *
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot import (
    LineBotApi, WebhookHandler
)
from db_access import db_connect
from local_config import key_list
from os.path import join, dirname
from dotenv import load_dotenv
from pathlib import Path
import os
import psycopg2
import csv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# 環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ['YOUR_CHANNEL_ACCESS_TOKEN']
YOUR_CHANNEL_SECRET = os.environ['YOUR_CHANNEL_SECRET']

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
FILE_PATH = './{}.csv'


# コンテンツのチェック
def cont_check(column):
    try:
        contents = {
            '曲名': column['曲名'],
            '該当URL': column['該当URL'],
            '検索用頭文字': column['検索用頭文字'],
            'アーティスト名_アニメ名': column['アーティスト名_アニメ名'],
            'VOCALOID': column['VOCALOID'],
            '音源': column['音源'],
            '放送日': column['放送日'],
            '配信PF': column['配信PF'],
            '配信タイトル': column['配信タイトル'],
            '配信URL': column['配信URL']
            # '登録日': str(datetime.date.today())
        }
        # print(contents)
        return contents
    except Exception as e:
        # 入れコン終了
        print(e)
        print('csvのヘッダーに誤りがあるようです。申し訳ありませんが確認をお願いします。')


# 配信タイトルに重複がないかチェック
def my_db_check(con, title_list):
    try:
        with con.cursor() as cur:
            for title in title_list:
                sql = f"select song_title stream_title from song_list where stream_title = '{title}';"
                cur.execute(sql)
                row = cur.fetchone()
                con.commit()
        # print(row)
        return row
    except Exception as e:
        print(e)
        return -1


# dbにお歌データを登録
def my_db_insert(con, insert_list):
    try:
        with con.cursor() as cur:
            for insert in insert_list:
                sql = f"insert into song_list values('{insert[0]}','{insert[1]}','{insert[2]}','{insert[3]}','{insert[4]}','{insert[5]}','{insert[6]}','{insert[7]}','{insert[8]}','{insert[9]}', current_date);"
                cur.execute(sql)
                con.commit()
        return True
    except Exception as e:
        print(e)
        return False


# csv から読み取ってDBにinsertする
def insert_song_date(con, event):
    csv_list = []
    file_content = []
    title_list = []
    insert_list = []

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

    # 配信タイトルとインサートリストを取得
    for column in csv_list:
        arry = []
        file_content = cont_check(column)
        title_list.append(file_content['配信タイトル'])
        for key in key_list:
            arry.append(file_content[key])
        insert_list.append(arry)

    check_result = my_db_check(con, list(set(title_list)))
    if check_result == None:
        result = my_db_insert(con, insert_list)
        if not result:
            message = 'DB登録でエラーが発生しました。'
            print(message)
            return message

        message = 'DBに登録されました!ありがとうございます!!'
        print(message)
        return message
    elif check_result != -1:
        message = 'エラーが発生しました。時間を置いて再度お試しください。'
        print(message)
        return message
    else:
        message = 'すでに登録されているようです。ご確認ください。'
        print(message)
        return message
