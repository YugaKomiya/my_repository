# -*- coding: utf-8 -*-

# 必要モジュールの読み込み
from flask import Flask, request, abort
# from linebot.models import (
#    MessageEvent, TextMessage, TextSendMessage, RichMenu, RichMenuSize, RichMenuArea, RichMenuBounds, URIAction, MessageAction
# )

from linebot.models import *

from linebot.exceptions import (
    InvalidSignatureError
)
from linebot import (
    LineBotApi, WebhookHandler
)
# from richmenu import RichMenu, RichMenuManager
from os.path import join, dirname
from dotenv import load_dotenv
import os
import pprint
import psycopg2

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# 変数appにFlaskを代入。インスタンス化
app = Flask(__name__)

# 環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ['YOUR_CHANNEL_ACCESS_TOKEN']
YOUR_CHANNEL_SECRET = os.environ['YOUR_CHANNEL_SECRET']

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

# rmm = RichMenuManager(YOUR_CHANNEL_ACCESS_TOKEN)


# 実行するとhello worldと表示される
@app.route("/")
def hello_world():
    return "hello world!"


def createRichmenu():
    result = False
    try:
        rich_menu_to_create = RichMenu(
            size=RichMenuSize(width=1200, height=405),
            selected=False,
            name="nice_richmenu",
            chat_bar_text="Tap to open",
            areas=[
                RichMenuArea(
                    bounds=RichMenuBounds(x=0, y=0, width=400, height=405),
                    action=MessageAction(text='メッセージ_01')
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=400, y=0, width=400, height=405),
                    action=MessageAction(text='メッセージ_02')
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=800, y=0, width=400, height=405),
                    action=MessageAction(text='メッセージ_03')
                )
            ]
        )

        rich_menu_id = line_bot_api.create_rich_menu(
            rich_menu=rich_menu_to_create)
        print(rich_menu_id)

        # upload an image for rich menu
        # image = 'richmenu.jpg'
        path = 'kemuricolor.PNG'

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
# line_bot_api.delete_rich_menu(rich_menu_list[0]['richMenuId'])

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
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@ handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


# ポート番号の設定
if __name__ == "__main__":
    app.run()
    # port = int(os.getenv('PORT'))
    # app.run(host="0.0.0.0", port=port)
