
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import os
import random

app = Flask(__name__)

#環境変数取得
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
randomResList = [
				 'いま大体売れてる本自分が作っているんで。',
				 '絶対的成果主義ならランチは食べない。時間が惜しいからだ。お前らは家畜ではない。',
				 '箕輪編集室は、圧倒的な実働部隊！',
				 'モノをどう編集するか、キュレーションの時代。編集力はすべてに通ず。',
				 '瞬間瞬間の思い付きを最速で形にしていく。',
				 '箕輪編集室は何が生まれるかは分からないラボ的な場所。',
				 '数は力。',
				 '箕輪編集室はある人にとっては、常に動いているカオス。ある人にとっては、ゆるやかな安らぎの場所。',
				 '各地方に拠点をつくりたい！！！地方の箕輪マフィア大募集！！！',
				 '多動力とは死ぬほど何かを突き詰める力。',
				 '失敗は最高のブランディング。失敗は高いハードルを超えようと思った時に起きるものだから。',
				 'せっかく「意識高い系」なら、あとはひたすら手を動かし、己の名を上げろ！傍観者になるな実践者たれ。',
				 '編集者とは才能のカクテルを飲める最高の仕事。',
				 '「努力」は「夢中」に勝てない',
				 '人脈を作るのは信頼を重ねるだけ。',
				 '選択肢があったらやったことがないことをやる',
				 '正しいことより楽しいことをしたい',
				 '己の名を上げろ！時代を作れ！',
				 '最初こそ、あえて高いところにいくべき',
				 '願うだけのやつ、言うだけのやつ、やるやつ、やりきるやつ。人はこの4パターン。',
				 'なんか仮想通貨とかカジノとかやってると月収分が瞬間で儲かったり失ったりして真面目に働くのがバカらしくなるけど、それでいいのだ。真面目に働くのがバカらしくなった後も、気がついたらやってしまっているものが本当の仕事だ。',
				 '好きが勝つ'
				 ]

# keyと一致する入力ならvalueを出力する用の辞書
resDictionary = {
"死ぬこと以外は":"かすり傷",
"読書という":"荒野"
}


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	
	targetKey = ""
	
	# 辞書に含まれるものは特定の言葉を返す
	for key in resDictionary:
		#		if event.message.text.find(key) != -1:
		if event.message.text == key:
			targetKey = key
			break

	if targetKey != "":
		reply = resDictionary[targetKey]
	else:
		#　特定の単語が入っていなければリストからランダムで返信する
		reply = random.choice(randomResList)
			
	# デバッグ用ログ出力
	#	print(reply)

	line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply))


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
