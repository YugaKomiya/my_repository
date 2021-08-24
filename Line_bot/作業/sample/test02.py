# -*- coding: utf-8 -*-
# python から SQL を渡すテスト
from os.path import join, dirname
from dotenv import load_dotenv
import os
import psycopg2

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


# DB接続
def connect():
    DB_NAME = os.environ['DB_NAME']
    USER = os.environ['USER']
    PASSWORD = os.environ['PASSWORD']

    con = psycopg2.connect('host=' + 'localhost' +
                           ' port=' + '5432' +
                           ' dbname=' + DB_NAME +
                           ' user=' + USER +
                           ' password=' + PASSWORD)

    return con


def select_execute(con, sql):
    with con.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()

    return rows


if __name__ == '__main__':
    con = connect()

    str = input()
    while len(str) < 2:
        print('頭2文字(ひらがな)以上から検索可能です')
        str = input()

    sql = f"select song_title, song_url, initial, day, stream_title from song_list where song_title like '{str}%' or initial like '{str}%'  ORDER BY day asc"

    result = select_execute(con, sql)

    for res in result:
        print(f'曲名:{res[0]}\n配信日:{res[3]}\n枠名:{res[4]}\nurl:{res[1]}')
        print('\n')

    print(len(result))

    con.close()
