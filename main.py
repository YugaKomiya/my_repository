# -*- coding: utf-8 -*-
from __future__ import print_function
from dics import members
from get_data import get_twitter_profile, get_sheet_data
from tools import twitter_api
import time
import datetime
#import pickle
import os
import gspread
import tweepy
from apscheduler.schedulers.blocking import BlockingScheduler
sched = BlockingScheduler()
api = twitter_api()

rn_time = 1  # 何分ごとに概要欄の数値を取得するか

all_num = len(members)

# Twitterプロフの変更を検知してツイートする


def tw_log_notification():
    print('tw_log_notification')
    start_ = time.time()
    contents = {}
    for name in members:
        contents.update({name: get_twitter_profile(name)})

    # 古いデータをsheetから取り出す
    worksheet = get_sheet_data()
    cell_dict = {}
    cell_dict = worksheet.get_all_records(
        empty2zero=False, head=1, default_blank='')

    if not cell_dict:
        # cell_dictが空の場合、取ったデータを書き出す
        for row, name in enumerate(members):
            col = 1
            for key in contents[name].keys():
                worksheet.update_cell(row+2, col, contents[name][key])
                col += 1
        # sheetから取り出す
        cell_dict = worksheet.get_all_records(
            empty2zero=False, head=1, default_blank='')

    old_contents = {}
    for num, name in enumerate(members):
        old_contents.update({name: cell_dict[num]})

    # ツイートする
    def make_tweet(name, key):
        # name_ = name + 'さん'
        tweet = '{} が変更されました。\n\n'.format(key)
        if key == '概要欄':
            print('概要欄')
            if len(tweet) + len(contents[name][key]) < 160:
                tweet += contents[name][key]
                try:
                    api.update_status(status=tweet)
                    print('tweeted_1')
                except tweepy.error.TweepError:
                    dir(tweepy.error.TweepError)
                    print('error_1')
            else:
                try:
                    tweet += '変更されました。長いのでご報告のみになります。'
                    api.update_status(status=tweet)
                    print('tweeted_2')
                except tweepy.error.TweepError:
                    dir(tweepy.error.TweepError)
                    print('error_2')
        else:
            print('other_update')

    # 旧と新データの比較
    # 変更されていたらmake_tweet でツイート
    # Twitterから取ってきたをspreadsheetに書き出す
    for row, name in enumerate(members):
        col = 1
        for key in contents[name].keys():
            if contents[name][key] != old_contents[name][key]:
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
