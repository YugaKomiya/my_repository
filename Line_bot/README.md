"あるYoutubeチャンネルの数多あるお歌配信の中から、お歌リストを用いて特定のお歌をLineから検索できるようにするbot"</br>
と言ったな…。あれは嘘だ！！！！(※本当です)</br>
# 推しのYoutubeのチャンネルにある歌配信の中から指定のお歌をすぐに見つけたい!

## 心の叫び
Youtubeで配信者として活動している"推し"はめちゃくちゃ歌がうまい！！活動の中で配信で歌配信をすることもある。我々、リスナーとしては配信後、</br>
"あの配信で歌ってた曲をもう一度聞きたい"</br>
と思うのはよくあることである。</br>
しかし！！歌枠がいっぱいあってお歌を探すことができない！！</br>
歌枠を開いて、特定のお歌を探すのはめんどい！！</br>
お歌リストというcsvでまとめてくれた方もいるが、スマホだと扱いずらい！！</br>
ここではLineの対話型UIを用いて、スマホ向けの検索botを組む!!</br>

## 使用するもの
- Python3.9
- Heroku
- Line Messaging API
- PostgreSQL
- Youtube API
- Google Drive API

## 参考
- [LINE Developers](https://developers.line.biz/ja/)
- [Herokuでサンプルボットを作成する](https://developers.line.biz/ja/docs/messaging-api/building-sample-bot-with-heroku/)
- [素人が1ヶ月でLINE BOTに挑戦する毎日note.](https://note.com/96nz/m/md28b901bbba5)
- [line/line-bot-sdk-python](https://github.com/line/line-bot-sdk-python)
- [Canva](https://www.canva.com/)

## Special Thanks
DBにはリスナーさんが作成したお歌リストを入れました。</br>
これがなければ僕はこの仕組みを作れなかった。本当にありがとうございます。</br>
お歌配信アーカイブにタイムテーブルを作成してくれるリスナーさん、</br>
配信に来られてるリスナーさん全てのBigLoveと熱量に最大の敬意と感謝を。</br>