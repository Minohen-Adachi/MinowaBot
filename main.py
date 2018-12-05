#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import random
import sys
import urllib.request
import requests

from bs4 import BeautifulSoup
from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (MessageEvent, SourceUser, TextMessage,
                            TextSendMessage, VideoMessage, VideoSendMessage)
from selenium import webdriver
from urllib.parse import urlparse

app = Flask(__name__)

# 環境変数取得 
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
driver_path = os.environ["CHROME_DRIVER_PATH"]
chrome_binary_location = os.environ["CHROME_BINARY_LOCATION"]

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

def navigate(driver):
    print('Navigating...')

    url = 'https://note.mu/hashtag/箕輪編集室?f=popular'
    p = urlparse(url)
    query = urllib.parse.quote_plus(p.query, safe='=&')
    url = '{}://{}{}{}{}{}{}{}{}'.format(
        p.scheme, p.netloc, p.path,
        ';' if p.params else '', p.params,
        '?' if p.query else '', query,
        '#' if p.fragment else '', p.fragment)

    driver.get(url)  # noteのトップページを開く。
    assert 'note' in driver.title  # タイトルに'note'が含まれていることを確認する。
    print(driver.title)

def scrape_posts(driver):
    print('Scraping start...')

    posts = []

    # すべての文章コンテンツを表すh3要素について反復する。
    for h3 in driver.find_elements_by_xpath("//h3[@class='renewal-p-cardItem__title']"):
        # URL、タイトル、を取得して、dictとしてリストに追加する。
        posts.append({
            'title': h3.find_element_by_css_selector('a').text,
            'url': h3.find_element_by_css_selector('a').get_attribute('href'),
        })
        print(h3.find_element_by_css_selector('a').text)
        print(h3.find_element_by_css_selector('a').get_attribute('href'))

    print('Scraping end...')
    
    return posts


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
    "読書という": "荒野",
    "たった一人の": "熱狂"
}


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    # メッセージが送られてきたときの処理

    # 辞書に含まれるものは特定の言葉を返す
    for key, value in resDictionary.items():
        # keyが含まれていてvalueが含まれていないとき
        if key in event.message.text and value not in event.message.text:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=value))
            break

    # 勝算というフレーズが入っていたとき
    if '勝算' in event.message.text:
        # user名を取得
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            # user名
            name = profile.display_name
            # 「(user名)の勝算！」と返却する。
            reply = '{0}の勝算！'.format(name)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply))

    # 2.0というフレーズが入っていたとき
    elif '2.0' in event.message.text:
        # user名を取得
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            # user名
            name = profile.display_name
            # 「(user名)の勝算！」と返却する。
            reply = '{0}2.0'.format(name)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply))

    # 箕輪編集室の情報を返却
    elif '箕輪編集室' == event.message.text:
        r = requests.get("https://camp-fire.jp/projects/view/34264")
        soup = BeautifulSoup(r.content, "html.parser")
        # 箕輪編集室の現在のパトロン数
        numOfMember = soup.select("strong.number")[0].getText()
        # 箕輪編集室の現在の空き人数
        num = 0
        for i in soup.select("div.limited.rfloat"):
            # OUT OF STOCK でないとき
            if '残り' in i.getText():
                n = i.getText().replace('残り：', '').replace('人まで', '')
                num += int(n)
        if num == 0:
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(
                        text='箕輪編集室はこちら。'), TextSendMessage(
                        text='https://camp-fire.jp/projects/view/34264'), TextSendMessage(
                        text='現在{0}です。満員御礼！' .format(
                            numOfMember, num))])
        else:
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(
                        text='箕輪編集室はこちら。'), TextSendMessage(
                        text='https://camp-fire.jp/projects/view/34264'), TextSendMessage(
                        text='現在{0}です。{1}人空きがあります。' .format(
                            numOfMember, num))])

    # noteの#箕輪編集室の人気記事の情報を返却
    elif 'note' == event.message.text:

        from selenium.webdriver.chrome.options import Options
        options = Options()
        # Heroku以外ではNone
        # if chrome_binary_path: options.binary_location = chrome_binary_path
        options.binary_location = chrome_binary_location
        options.add_argument('--headless')
        
        driver = webdriver.Chrome(executable_path=driver_path, options=options)
        # driver = webdriver.Chrome(options=options)
        
        driver.set_window_size(800, 600)  # ウィンドウサイズを設定する。

        navigate(driver)  # noteのトップページに遷移する。
        posts = scrape_posts(driver)  # 文章コンテンツのリストを取得する。

        print('出力開始ログ')

        for post in posts:
            print(post)

        print('出力開始LINE')

        # コンテンツの情報を表示する。
        for post in posts:
            line_bot_api.reply_message(
                event.reply_token, 
                    TextSendMessage(
                        text=post))


    elif 'ドークショ' in event.message.text or 'ドクショ' in event.message.text or\
            'コウヤ' in event.message.text:
        messages = [
            TextSendMessage(
                text='ドークショドクショドークショ コウヤ（＾Ｏ＾）') for i in range(4)]
        messages.append(TextSendMessage(text='ドークショドクショデジッセンダ（＾Ｏ＾）'))
        line_bot_api.reply_message(
            event.reply_token,
            messages)

    else:
        # 特定の単語が入っていなければリストからランダムで返信する
        reply = random.choice(randomResList)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply))


if __name__ == "__main__":
    # app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
