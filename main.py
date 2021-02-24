# -*- coding: utf-8 -*-
from __future__ import print_function
from dics import members
from get_data import get_twitter_profile
from tools import twitter_api, google_api, update_sheet, download_image, concatenate_icon, tweet_with_imgs
import time
import datetime
import os
import gspread
import tweepy
from apscheduler.schedulers.blocking import BlockingScheduler
sched = BlockingScheduler()
api = twitter_api()

rn_time = 1  # 何分ごとにプロフの数値を取得するか
all_num = len(members)

icon_img = './{}_icon_{}.png'
banner_img = './{}_banner_{}.png'


# Twitterプロフの変更を検知してツイートする
def tw_log_notification():
    print('tw_log_notification')
    start_ = time.time()
    contents = {}
    for name in members:
        # プロフ情報を取得
        contents.update({name: get_twitter_profile(name)})
        # アイコンとヘッダーの画像を保存
        # ローカルに保存
        if not os.path.exists(icon_img.format('old', name)):
            download_image(contents[name]['アイコン'],
                           icon_img.format('old', name))
        if not os.path.exists(banner_img.format('old', name)):
            download_image(contents[name]['ヘッダー'],
                           banner_img.format('old', name))

    # 古いデータをsheetから取り出す
    worksheet = google_api()
    cell_dict = []
    cell_dict = worksheet.get_all_records(
        empty2zero=False, head=1, default_blank='')

    # cell_dict が空の場合、cell_dict と contents の 要素数が異なる場合
    # 取得したデータを書き出す
    if not cell_dict or len(cell_dict) != len(contents):
        cell_dict = update_sheet(contents, worksheet)

    # 要素数が異なる場合更新
    for num, name in enumerate(members):
        if len(contents[name]) != len(cell_dict[num]):
            cell_dict = update_sheet(contents, worksheet)
            break

    # sheetからプロフ情報を取る
    old_contents = {}
    for num, name in enumerate(members):
        old_contents.update({name: cell_dict[num]})

    # ツイートする
    def make_tweet(name, key):
        print('{} {}\n'.format(name, key))
        tweet = '{}さんが{}を変更されました。\n\n'.format(name, key)
        if key == 'bio':
            print(key)
            if len(tweet) + len(contents[name][key]) < 160:
                # tweet += contents[name][key]
                try:
                    tweet += contents[name][key]
                    api.update_status(status=tweet)
                    print(tweet)
                except tweepy.error.TweepError:
                    dir(tweepy.error.TweepError)
                    print('error_prof_1')
            else:
                try:
                    tweet += '長いのでご報告のみになります。\n'
                    api.update_status(status=tweet)
                    print(tweet)
                except tweepy.error.TweepError:
                    dir(tweepy.error.TweepError)
                    print('error_prof_2')

        elif key == 'アイコン':
            print(key)
            download_image(contents[name][key], icon_img.format('new', name))
            concatenate_icon(icon_img.format('old', name), icon_img.format(
                'new', name), icon_img.format('tw', name))
            tweet_with_imgs(tweet, icon_img.format('tw', name))
            os.rename(icon_img.format('new', name),
                      icon_img.format('old', name))

        elif key == 'ヘッダー':
            print(key)
            download_image(contents[name][key], banner_img.format('new', name))
            tweet_with_imgs(tweet, [banner_img.format(
                'old', name), banner_img.format('new', name)])
            os.rename(banner_img.format('new', name),
                      banner_img.format('old', name))

        else:
            if key in ['名前', '場所', 'URL']:
                print(key)
                try:
                    tweet += '{}\n'.format(old_contents[name][key])
                    tweet += '  ↓\n'
                    tweet += '{}\n'.format(contents[name][key])
                    api.update_status(status=tweet)
                    print(tweet)
                except tweepy.error.TweepError:
                    dir(tweepy.error.TweepError)
                    print('error_other_1')

    # 旧と新データの比較
    # 変更されていたら make_tweet でツイート
    # Twitterから取ってきたdataをspreadsheetに書き出す
    for row, name in enumerate(members):
        col = 1
        for key in contents[name].keys():
            if contents[name][key] != old_contents[name][key]:
                if contents[name]['場所'] == '':
                    break
                make_tweet(name, key)
                # 更新されていたらTwitterから取ってきたデータをspreadsheetに書き出す
                worksheet.update_cell(row+2, col, contents[name][key])
            col += 1

    measure_time = time.time() - start_
    if measure_time > 60 * rn_time:
        print('Too hard work on tw_log_notification')


if __name__ == '__main__':
    start_ = time.time()
    print('Start work : {}'.format(datetime.datetime.utcnow()))
    print('test tw_log_not : {} : {}'.format(all_num, members))
    tw_log_notification()
    sched.add_job(tw_log_notification, 'interval', minutes=rn_time)
    print(time.time() - start_)
    print('sched work start')
    sched.start()
