# -*- coding: utf-8 -*-
#!./line/bin/python

# 必要モジュールの読み込み
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot import (
    LineBotApi, WebhookHandler
)
from flask import Flask, request, abort
import os
from os.path import join, dirname
from dotenv import load_dotenv
import psycopg2
import pprint

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# 変数appにFlaskを代入。インスタンス化
app = Flask(__name__)

# 環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ['YOUR_CHANNEL_ACCESS_TOKEN']
YOUR_CHANNEL_SECRET = os.environ['YOUR_CHANNEL_SECRET']

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


# Herokuログイン接続確認のためのメソッド
# Herokuにログインすると「hello world」とブラウザに表示される
@app.route("/")
def hello_world():
    return "hello world!"


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


# 返事取得関数（今は暫定で日付返す関数）
def get_response_message(mes_from, con):
    if len(mes_from) < 2:
        return -1

    sql = f"select song_title, song_url, initial, day, stream_title from song_list where song_title like '{mes_from}%' or initial like '{mes_from}%'  ORDER BY day asc"
    result = select_execute(con, sql)

    return result


# select文実行
def select_execute(con, sql):
    with con.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()

    return rows


# ユーザーからメッセージが送信された際、LINE Message APIからこちらのメソッドが呼び出される。
@app.route("/callback", methods=['POST'])
def callback():
    # リクエストヘッダーから署名検証のための値を取得
    signature = request.headers['X-Line-Signature']

    # リクエストボディを取得
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 署名を検証し、問題なければhandleに定義されている関数を呼び出す。
    try:
        handler.handle(body, signature)
    # 署名検証で失敗した場合、例外を出す。
    except InvalidSignatureError:
        abort(400)
    # handleの処理を終えればOK
    return 'OK'


# LINEでMessageEvent（普通のメッセージを送信された場合）が起こった場合に、
# def以下の関数を実行します。
# reply_messageの第一引数のevent.reply_tokenは、イベントの応答に用いるトークンです。
# 第二引数には、linebot.modelsに定義されている返信用のTextSendMessageオブジェクトを渡しています。
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    con = db_connect()
    sql_result = get_response_message(event.message.text, con)
    print(len(sql_result))
    url_list = []
    txt_list = []

    # lineの仕様により、reply_messageで返信可能なメッセージ数が
    # 最大5件のための見苦しい対応をしています。

    if sql_result == -1:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='(ひらがな)2文字以上入力してね'))
    else:
        """
        if len(sql_result) == 1:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f'曲名:{sql_result[0][0]}\n配信日:{sql_result[0][3]}\n枠名:{sql_result[0][4]}\nurl:{sql_result[0][1]}'))

        elif len(sql_result) == 2:
            line_bot_api.reply_message(
                event.reply_token,
                [TextSendMessage(
                    text=f'曲名:{sql_result[0][0]}\n配信日:{sql_result[0][3]}\n枠名:{sql_result[0][4]}\nurl:{sql_result[0][1]}'),
                 TextSendMessage(text=f'曲名:{sql_result[1][0]}\n配信日:{sql_result[1][3]}\n枠名:{sql_result[1][4]}\nurl:{sql_result[1][1]}')])

        elif len(sql_result) == 3:
            line_bot_api.reply_message(
                event.reply_token,
                [TextSendMessage(
                    text=f'曲名:{sql_result[0][0]}\n配信日:{sql_result[0][3]}\n枠名:{sql_result[0][4]}\nurl:{sql_result[0][1]}'),
                 TextSendMessage(
                     text=f'曲名:{sql_result[1][0]}\n配信日:{sql_result[1][3]}\n枠名:{sql_result[1][4]}\nurl:{sql_result[1][1]}'),
                 TextSendMessage(text=f'曲名:{sql_result[2][0]}\n配信日:{sql_result[2][3]}\n枠名:{sql_result[2][4]}\nurl:{sql_result[2][1]}')])

        elif len(sql_result) == 4:
            line_bot_api.reply_message(
                event.reply_token,
                [TextSendMessage(
                    text=f'曲名:{sql_result[0][0]}\n配信日:{sql_result[0][3]}\n枠名:{sql_result[0][4]}\nurl:{sql_result[0][1]}'),
                 TextSendMessage(
                     text=f'曲名:{sql_result[1][0]}\n配信日:{sql_result[1][3]}\n枠名:{sql_result[1][4]}\nurl:{sql_result[1][1]}'),
                 TextSendMessage(
                     text=f'曲名:{sql_result[2][0]}\n配信日:{sql_result[2][3]}\n枠名:{sql_result[2][4]}\nurl:{sql_result[2][1]}'),
                 TextSendMessage(text=f'曲名:{sql_result[3][0]}\n配信日:{sql_result[3][3]}\n枠名:{sql_result[3][4]}\nurl:{sql_result[3][1]}')])

        elif len(sql_result) == 5:
            line_bot_api.reply_message(
                event.reply_token,
                [TextSendMessage(
                    text=f'曲名:{sql_result[0][0]}\n配信日:{sql_result[0][3]}\n枠名:{sql_result[0][4]}\nurl:{sql_result[0][1]}'),
                 TextSendMessage(
                     text=f'曲名:{sql_result[1][0]}\n配信日:{sql_result[1][3]}\n枠名:{sql_result[1][4]}\nurl:{sql_result[1][1]}'),
                 TextSendMessage(
                     text=f'曲名:{sql_result[2][0]}\n配信日:{sql_result[2][3]}\n枠名:{sql_result[2][4]}\nurl:{sql_result[2][1]}'),
                 TextSendMessage(
                     text=f'曲名:{sql_result[3][0]}\n配信日:{sql_result[3][3]}\n枠名:{sql_result[3][4]}\nurl:{sql_result[3][1]}'),
                 TextSendMessage(text=f'曲名:{sql_result[4][0]}\n配信日:{sql_result[4][3]}\n枠名:{sql_result[4][4]}\nurl:{sql_result[4][1]}')])
        """
        if len(sql_result) == 0:
            line_bot_api.reply_message(
                event.reply_token,
                [TextSendMessage(text='ヒットしませんでした')])

        else:
            for res in sql_result:
                txt = f'曲名:{res[0]}\n配信日:{res[3]}\n枠名:{res[4]}\nurl:{res[1]}\n'
                txt_list.append(f'{txt}')

            str = ''.join(txt_list)
            line_bot_api.reply_message(
                event.reply_token,
                [TextSendMessage(text=f'{len(sql_result)}件ヒットしました'), TextSendMessage(text=str)])


# ポート番号の設定
if __name__ == "__main__":
    app.run()
    #port = int(os.getenv('PORT'))
    #app.run(host="0.0.0.0", port=port)
