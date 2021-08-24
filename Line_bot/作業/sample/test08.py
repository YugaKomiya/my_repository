# -*- coding: utf-8 -*-
# csvから読み取って登録日を足してinseretのお試し

#from linebot.models.responses import Content
from os.path import join, dirname
from dotenv import load_dotenv
from local_config import key_list
import os
import sys
import csv
import pprint
import psycopg2

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


# DB接続
def db_connect():
    try:
        HOST = os.environ['HOST']
        PORT_DB = os.environ['PORT_DB']
        DB_NAME = 'test'  # os.environ['DB_NAME']
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
        # print('db_connect_error')


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
                sql = f"select song_title stream_title from test_song_list where stream_title = '{title}';"
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
                sql = f"insert into test_song_list values('{insert[0]}','{insert[1]}','{insert[2]}','{insert[3]}','{insert[4]}','{insert[5]}','{insert[6]}','{insert[7]}','{insert[8]}','{insert[9]}', current_date);"
                cur.execute(sql)
                con.commit()

    except Exception as e:
        print(e)  # ここでpush通知したい


# csv から読み取ってDBにinsertする
def insert_song_date():
    con = db_connect()
    csv_list = []
    file_content = []
    title_list = []
    insert_list = []
    file_name = './test.csv'

    # ファイルを開く
    try:
        with open(file_name, 'r') as rf:
            for row in csv.DictReader(rf):
                csv_list.append(row)
    except Exception:
        print('read_csv_error')

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
        my_db_insert(con, insert_list)
    else:
        # リプライ すでに登録されているようです 的なメッセージを返す
        print('already registered')


if __name__ == "__main__":
    insert_song_date()
