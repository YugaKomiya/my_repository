# -*- coding: utf-8 -*-
# 画面を作るやつ、反応するやつ

from linebot.models import *
from linebot.exceptions import (
	InvalidSignatureError, LineBotApiError
)
from linebot import (
	LineBotApi, WebhookHandler
)
from flask import Flask, request, abort
from sql_generate import song_title_choice, date_template_make, date_choice, stream_title_choice, artist_choice
from local_config import TEXT_00, TEXT_01, TEXT_02, TEXT_03
from db_access import db_connect, update_state, select_execute, id_search, id_delete
from insert_data import insert_song_data
from os.path import join, dirname
from dotenv import load_dotenv
import os

# .envファイルの読み込み
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# lineチャンネルのアクセストークン、チャンネルシークレット
# 環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ['YOUR_CHANNEL_ACCESS_TOKEN']
YOUR_CHANNEL_SECRET = os.environ['YOUR_CHANNEL_SECRET']

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

USER_ID = 0
defo_STATE = 0
#STATE = 0
MY_LINE_ID = os.environ['MY_LINE_ID']

# DB接続
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
					action=MessageAction(text=TEXT_02)  # アーティスト名から検索
				),
				RichMenuArea(
					bounds=RichMenuBounds(x=800, y=405, width=400, height=405),
					action=MessageAction(text=TEXT_03)  # formatDL リンク
				)
			]
		)

		rich_menu_id = line_bot_api.create_rich_menu(
			rich_menu=rich_menu_to_create)
		print(rich_menu_id)

		# upload an image for rich menu
		path = 'richmenu03.png'

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
#print(len(rich_menu_list))

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
	#print(STATE)

	if len(message_txt) < 2:
		message = '(ひらがな)2文字以上入力してね'
		reply_message(event, message)

	elif message_txt == TEXT_00:
		state = 0
		STATE = mendo(con, USER_ID, state)
		# message = song_title_choice(USER_ID)
		message = '曲名を入力してね'
		reply_message(event, message)

	elif message_txt == TEXT_01:
		state = 1
		STATE = mendo(con, USER_ID, state)
		# <- この message は日付選択のメニューをつくるので変えたらだめ
		messages = date_template_make()
		line_bot_api.reply_message(
			event.reply_token,
			messages
		)

	elif message_txt == TEXT_03: # フォーマットダウンロード
		#state = 3
		message_1 = '【フォーマット説明】 \n曲名:曲名を記入\n\n該当URL: 配信URLの最後に「?t=秒数」をいれたもの。(youtube限定)\n配信の中で上記のお歌を歌った箇所を秒数で表し、配信URLの末尾につけ記入してください\n\nツイキャスやニコ生なら配信URLそのまま\n検索用頭文字: 曲名からひらがなで頭文字3文字以内で記入してください\n\n例) ファンサ -> ふぁん、ロキ -> ろき\n\nアーティスト名: 原曲の歌手やユニット、ボカロならPを記入\n\nVOCALOID: ボーカロイドを記入\n\n音源: Inst アカペラ Onseなど\n\n放送日: 配信日時 例:2021-07-09\n\n配信PF: youtube -> YT\nツイキャス -> TC\nニコ生 -> nico\n\n配信タイトル: 配信名を記入\n\n配信URL: 配信名と関連する通常のURL'
		message_2 = os.environ['FORMAT_CSV']

		line_bot_api.reply_message(
			event.reply_token,
			[TextSendMessage(text=message_1),
			TextSendMessage(text=message_2)]
		)
		STATE = mendo(con, USER_ID, state=0)

	elif message_txt == TEXT_02: # アーティストから検索
		state = 2
		STATE = mendo(con, USER_ID, state)
		message = 'アーティスト名を入力してね'
		reply_message(event, message)

	else:
		if STATE == 0:
			try:
				sql = song_title_choice(event)
				sql_result_recive(event, sql)

			except LineBotApiError:
				print('00')
				message = 'エラーが発生したようです。時間を置いて再度お試しください。'
				reply_message(event, message)
				error_mes = f"{STATE}\n{message_txt}\nerror_code=00"
				push_error_message(error_mes)

		elif STATE == 1:
			message = '日時指定メニューから日付を選択してください'
			reply_message(event, message)
			# def handle_postback で 日付入力を受け付ける
			# sql_result_recive(event, sql)
			# message = '日付を選べ'
			# reply_message(event, message)
		
		elif STATE == 2:
			try:
				sql = artist_choice(event)
				sql_result_recive(event, sql)

			except LineBotApiError:
				print('03')
				message = 'エラーが発生したようです。時間を置いて再度お試しください。'
				reply_message(event, message)

				error_mes = f"{STATE}\n{message_txt}\nerror_code=03"
				push_error_message(message)

		elif STATE == 3:
			message = '他項目から検索ください。'
			reply_message(event, message)

		else:
			rep_mes = 'errorが発生しました。時間を置いて再度お試しください。'
			reply_message(event, rep_mes)
			error_mes = f'{STATE},\n {message_txt},\n謎エラー'
			push_error_message(error_mes)


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
	try:
		if len(sql_result) == 0:
			line_bot_api.reply_message(
				event.reply_token,
				[TextSendMessage(text='ヒットしませんでした')])

		else:
			for res in sql_result:
				txt = f'曲名:{res[0]}\nアーティスト名:{res[1]}\n配信日:{res[2]}\n{res[3]}'
				txt_list.append(f'{txt}')

			str = '\n\n'.join(txt_list)
			line_bot_api.reply_message(
				event.reply_token,
				[TextSendMessage(text=f'{len(sql_result)}件ヒットしました'), TextSendMessage(text=str)])

	except LineBotApiError:
		print('04')
		message = 'エラーが発生したようです。時間を置いて再度お試しください。'
		reply_message(event, message)
		error_message = 'error_code = 04\n例外エラー'
		push_error_message(error_message)


# bot側から何か返信させるときはここ
def reply_message(event, message):
	line_bot_api.reply_message(
		event.reply_token,
		TextSendMessage(text=message)
	)


# 管理者にエラーの内容をpushする
def push_error_message(message):
	try:
		line_bot_api.push_message(
			MY_LINE_ID, TextSendMessage(text=message))
	except LineBotApiError as e:
		print(e)


# フォローされたらここ
@ handler.add(FollowEvent)
def follow_message(event):
	USER_ID = event.source.user_id # id取得
	STATE = id_search(con, USER_ID, defo_STATE)
	print(f'STATE: {STATE}')

	message = '友達登録ありがとうごさいます！曲名や日付から検索できるのでお試しください!!'
	reply_message(event, message)


# ブロックさたらここ
@ handler.add(UnfollowEvent)
def unfollow_message(event):
	USER_ID = event.source.user_id
	result = id_delete(con, USER_ID)
	if not result:
		print('delete error')
	print('delete success')


# fileを受け取ったら反応するのはここ
@handler.add(MessageEvent, message=FileMessage)
def file_recieve(event):
	file_event = event
	result = insert_song_data(con, file_event) # csv読み取ってインポート
	print(result)
	reply_message(file_event, result)


# 日付選択の際、ここで受け取る
@handler.add(PostbackEvent)
def handle_postback(event):
	if isinstance(event, PostbackEvent):
		# event.postback.params['date']  # dictのキーはmodeのもの
		try:
			sql = date_choice(event.postback.params['date'])
			sql_result_recive(event, sql)

		except LineBotApiError:
			#print('01')
			message = '処理に時間がかかっています。少し時間を置いてから再度お試しください。'
			reply_message(event, message)

			error_mes = f"{event.postback.params['date']}\n{sql}\nerror_code=01"
			push_error_message(error_mes)


# ポート番号の設定
if __name__ == "__main__":
	# app.run()
	port = int(os.getenv('PORT'))
	app.run(host="0.0.0.0", port=port)
	con.close()
	