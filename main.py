from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, SourceUser, VideoMessage, VideoSendMessage
)
import os
import random

app = Flask(__name__)

# 環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


@app.route("/callback", methods=['POST'])
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
        abort(400)

    return 'OK'


# ランダム返信用のリスト
randomResList = []

# random.txtから名言を読み込む
with open('random.txt', 'r') as f:
    # 一列ごとに読み込む
    for line in f:
        # 改行文字の削除
        stripedLine = line.rstrip()
        randomResList.append(stripedLine)

# keyと一致する入力ならvalueを出力する用の辞書
resDictionary = {
    "死ぬこと以外は": "かすり傷",
    "読書という": "荒野"
}


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    targetKey = ""
    # 辞書に含まれるものは特定の言葉を返す
    for key, value in resDictionary.items():
        #		if event.message.text.find(key) != -1:
        if key in event.message.text and value not in event.message.text:
            targetKey = key
            break

    if targetKey != "":
        reply = resDictionary[targetKey]
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply))

    elif '勝算' in event.message.text:
        # user名を取得
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            # user名
            name = profile.display_name
            reply = '{0}の勝算！'.format(name)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply))

    elif '箕輪編集室' == event.message.text:
        line_bot_api.reply_message(
            event.reply_token,
            [TextSendMessage(text='箕輪編集室はこちら'),
             TextSendMessage(text='https://camp-fire.jp/projects/view/34264')])

    elif 'ドークショ' in event.message.text or 'ドクショ' in event.message.text or 'コウヤ' in event.message.text:
        messages = [TextSendMessage(text='ドークショドクショドークショ コウヤ（＾Ｏ＾）') for i in range(4)]
        messages.append(TextSendMessage(text='ドークショドクショデジッセンダ（＾Ｏ＾）'))
        line_bot_api.reply_message(
            event.reply_token,
            messages)
    else:
        # 　特定の単語が入っていなければリストからランダムで返信する
        reply = random.choice(randomResList)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply))

        # デバッグ用ログ出力
        #	print(reply)

        # line_bot_api.reply_message(
        #     event.reply_token,
        #     TextSendMessage(text=reply))


if __name__ == "__main__":
    #    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
