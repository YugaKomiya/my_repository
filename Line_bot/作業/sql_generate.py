# -*- coding: utf-8 -*-
# 後ろで動いてるやつら
# sql文を生成する

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

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# 環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ['YOUR_CHANNEL_ACCESS_TOKEN']
YOUR_CHANNEL_SECRET = os.environ['YOUR_CHANNEL_SECRET']

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


# DatetimePickerTemplateAction から日付決定
def date_template_make():
    date_picker = TemplateSendMessage(
        alt_text='日付を選択',
        template=ButtonsTemplate(
            text='日付を選択',
            title='日付から配信タイトルを検索',
            actions=[
                DatetimePickerTemplateAction(
                    label='YYYY-MM-dd',
                    data='action=buy&itemid=1',
                    mode='date',
                    initial='2019-06-01',
                    min='2019-06-01',
                    max='2050-12-31'
                )
            ]
        )
    )
    return date_picker


# 曲名からsql文作成
def song_title_choice(event):
    mes = event.message.text
    sql = f"select song_title, artist_anime_name, day, song_url from song_list where pf = 'YT' and (song_title like '{mes}%' or initial like '{mes}%') ORDER BY day asc;"

    return sql


# 日付からsql文作成
def date_choice(date):
    sql = f"select song_title, artist_anime_name, day, song_url from song_list where pf = 'YT' and day = '{date}';"
    return sql


# 配信タイトル入力からsql文作成
def stream_title_choice(event):
    mes = event.message.text
    sql = f"select song_title, artist_anime_name, day, song_url from song_list where pf = 'YT' and stream_title = '{mes}%';"
    return sql


# アーティスト名からsql文作成
def artist_choice(event):
    mes = event.message.text
    sql = f"select song_title, artist_anime_name, day, song_url from song_list where pf = 'YT' and artist_anime_name like '%{mes}%' ORDER BY day asc;"

    return sql
