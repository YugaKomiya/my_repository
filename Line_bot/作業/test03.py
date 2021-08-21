# -*- coding: utf-8 -*-

# 必要モジュールの読み込み
from flask import Flask, request, abort

from linebot.models import *

from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot import (
    LineBotApi, WebhookHandler
)
from sql_generate import song_title_choice, date_choice, stream_title_choice, artist_choice, date_template_make
from os.path import join, dirname
from dotenv import load_dotenv
from local_config import TEXT_00, TEXT_01, TEXT_02, TEXT_03
from db_access import (db_connect, insert_state, update_state, get_response_message,
                       select_execute, id_search)
import os
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
    USER_ID = event.source.user_id
    id_search(con, USER_ID, state=0)

    if event.message.text == TEXT_00:
        id_search(con, USER_ID, state=0)
        message = song_title_choice(USER_ID)
        reply_message(event, message)

    elif event.message.text == TEXT_01:
        id_search(con, USER_ID, state=1)
        messages = date_template_make(USER_ID)
        line_bot_api.reply_message(
            event.reply_token,
            messages
        )

    elif event.message.text == TEXT_02:
        id_search(con, USER_ID, state=2)
        message = stream_title_choice(USER_ID)
        reply_message(event, message)

    elif event.message.text == TEXT_03:
        id_search(con, USER_ID, state=3)
        message = artist_choice(USER_ID)
        reply_message(event, message)

    else:
        reply_message(event, event.message.text)


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
        # print(event.postback.params['date'])
        date_choice(event.postback.params['date'], TEXT_01)


# ポート番号の設定
if __name__ == "__main__":
    app.run()
    # port = int(os.getenv('PORT'))
    # app.run(host="0.0.0.0", port=port)
