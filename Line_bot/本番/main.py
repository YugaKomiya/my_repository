# -*- coding: utf-8 -*-
# 画面を作るやつら
# 必要モジュールの読み込み
from flask import Flask, request, abort

from linebot.models import *

from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot import (
    LineBotApi, WebhookHandler
)
from sql_generate import song_title_choice, date_template_make, date_choice, stream_title_choice, artist_choice
from os.path import join, dirname
from dotenv import load_dotenv
from local_config import TEXT_00, TEXT_01, TEXT_02, TEXT_03
from db_access import db_connect, update_state, select_execute, id_search
import os
import sys
import pprint
import psycopg2

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# 環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ['YOUR_CHANNEL_ACCESS_TOKEN']
YOUR_CHANNEL_SECRET = os.environ['YOUR_CHANNEL_SECRET']

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

USER_ID = 0
STATE = 0
defo_STATE = 0
con = db_connect()

# 変数appにFlaskを代入。インスタンス化
app = Flask(__name__)


# 実行するとhello worldと表示される
@app.route("/")
def hello_world():
    return 'hello world!'


# リッチメニューを生成
def createRichmenu():
    result = False
    try:
        rich_menu_to_create = RichMenu(
            size=RichMenuSize(width=1200, height=810),
            selected=False,
            name='nice_richmenu',
            chat_bar_text='Tap to open',
            areas=[
                RichMenuArea(
                    bounds=RichMenuBounds(x=0, y=0, width=1200, height=405),
                    action=MessageAction(text=TEXT_00)  # 曲名から検索
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=0, y=405, width=400, height=405),
                    action=MessageAction(text=TEXT_01)  # 配信日から検索
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=400, y=405, width=400, height=405),
                    action=MessageAction(text=TEXT_02)  # 配信タイトルから検索
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=800, y=405, width=400, height=405),
                    action=MessageAction(text=TEXT_03)  # アーティスト名から検索
                )
            ]
        )

        rich_menu_id = line_bot_api.create_rich_menu(
            rich_menu=rich_menu_to_create)
        print(rich_menu_id)

        # upload an image for rich menu
        path = 'menu02.png'

        with open(path, 'rb') as f:
            line_bot_api.set_rich_menu_image(rich_menu_id, 'image/png', f)

        # set the default rich menu
        line_bot_api.set_default_rich_menu(rich_menu_id)

        result = True

    except Exception:
        result = False

    return result


# check for existing richmenu
rich_menu_list = line_bot_api.get_rich_menu_list()
print(rich_menu_list)
print(len(rich_menu_list))

if not rich_menu_list:
    result = createRichmenu()
    if not result:
        print('error')


@ app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info('Request body: ' + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print('Invalid signature. Please check your channel access token/channel secret.')
        abort(400)

    return 'OK'


# lineに入力されたものはここに入る
# ここで分岐させる
@ handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message_txt = event.message.text
    USER_ID = event.source.user_id
    STATE = id_search(con, USER_ID, defo_STATE)

    if len(message_txt) < 2:
        message = '(ひらがな)2文字以上入力してね'
        reply_message(event, message)

    if message_txt == TEXT_00:
        state = 0
        STATE = mendo(con, USER_ID, state)
        #message = song_title_choice(USER_ID)
        message = '曲名を入力してね'
        reply_message(event, message)

    elif message_txt == TEXT_01:
        state = 1
        STATE = mendo(con, USER_ID, state)
        # <- このmessage は日付選択のメニューをつくるので変えたらだめ
        messages = date_template_make(USER_ID)
        line_bot_api.reply_message(
            event.reply_token,
            messages
        )

    elif message_txt == TEXT_02:
        state = 2
        STATE = mendo(con, USER_ID, state)
        message = '配信タイトルを入力してね'
        reply_message(event, message)

    elif message_txt == TEXT_03:
        state = 3
        STATE = mendo(con, USER_ID, state)
        message = 'アーティスト名を入力してね'
        reply_message(event, message)

    elif message_txt == '初音ミク' or message_txt == '鏡音リン' or message_txt == '鏡音レン':
        message = '申し訳ありませんがこのワードは現在ご利用になれません。\n検索結果が大量に出力されてlineがパンクしてしまいます。\n申し訳ありませんが曲などから再度お探しください🙇‍♂️'
        reply_message(event, message)

    elif message_txt == '初音' or message_txt == '鏡音':
        message = '申し訳ありませんがこのワードは現在ご利用になれません。\n検索結果が大量に出力されてlineがパンクしてしまいます。\n申し訳ありませんが曲などから再度お探しください🙇‍♂️'
        reply_message(event, message)

    else:
        if STATE == 0:
            sql = song_title_choice(event)
            sql_result_recive(event, sql)

        # elif STATE == 1:
            # def handle_postback で 日付入力を受け付ける
            # sql_result_recive(event, sql)
            #message = '日付を選べ'
            #reply_message(event, message)

        elif STATE == 2:
            sql = stream_title_choice(event)
            sql_result_recive(event, sql)

        elif STATE == 3:
            sql = artist_choice(event)
            sql_result_recive(event, sql)

        else:
            message = 'このメッセージは意図しないものなので、見た方は速やかに管理者に連絡してください'
            reply_message(event, event.message.text)


# めんどい作業をまとめた
def mendo(con, USER_ID, state):
    update_state(con, USER_ID, state)
    state = id_search(con, USER_ID, state)
    return state


# sql実行結果を受け取っていいかんじにするやつ
def sql_result_recive(event, sql):
    txt_list = []
    # sql_result = get_response_message(con, event.message.text)
    sql_result = select_execute(con, sql)

    if len(sql_result) == 0:
        line_bot_api.reply_message(
            event.reply_token,
            [TextSendMessage(text='ヒットしませんでした')])

    else:
        for res in sql_result:
            txt = f'曲名:{res[0]}\n配信日:{res[3]}\n枠名:{res[4]}\nurl:{res[1]}\n'
            txt_list.append(f'{txt}\n')

        str = ''.join(txt_list)
        line_bot_api.reply_message(
            event.reply_token,
            [TextSendMessage(text=f'{len(sql_result)}件ヒットしました'), TextSendMessage(text=str)])


# bot側から何か返信させるときはここ
def reply_message(event, message):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message)
    )


# 日付選択の際、ここで受け取る
@handler.add(PostbackEvent)
def handle_postback(event):
    if isinstance(event, PostbackEvent):
        # event.postback.params['date']  # dictのキーはmodeのもの
        try:
            sql = date_choice(event, event.postback.params['date'])
            sql_result_recive(event, sql)
        except LineBotApiError:
            message = '処理に時間がかかっています。少し時間を置いてから再度お試しください。'
            print('error')
            reply_message(event, message)


# ポート番号の設定
if __name__ == "__main__":
    app.run()
    # port = int(os.getenv('PORT'))
    # app.run(host="0.0.0.0", port=port)
    con.close()
