# -*- coding: utf-8 -*-
# 後ろで動いてるやつら

# 必要モジュールの読み込み
from flask import Flask, request, abort
from linebot.models import *

from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot import (
    LineBotApi, WebhookHandler
)

from os.path import join, dirname
from dotenv import load_dotenv
from local_config import TEXT_01, TEXT_02, TEXT_03
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


"""
# 返事取得関数
def get_sql_exe(con, sql):
    if len(mes_from) < 2:
        return -1

    result = select_execute(con, sql)

    return result
"""


# select文実行
def select_execute(con, sql):
    with con.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    con.commit()

    return rows


# song_list とは異なる
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


def id_search(con, USER_ID, state):
    sql = f"select state from user_state where user_id = '{USER_ID}';"
    with con.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    con.commit()
    # print(rows)

    if len(rows) == 0:
        insert_state(con, USER_ID, state)
        id_search(con, USER_ID, state)

    return rows[0][0]
