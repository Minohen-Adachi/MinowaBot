#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from selenium import webdriver
from time import sleep

def main():
    """
    メインの処理。
    """

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)  # 今は chrome_options= ではなく options=
    driver.set_window_size(800, 600)  # ウィンドウサイズを設定する。
    navigate(driver)  # noteのトップページに遷移する。
    posts = scrape_posts(driver)  # 文章コンテンツのリストを取得する。

    # コンテンツの情報を表示する。
    for post in posts:
        print(post)

    return posts


def navigate(driver):
    """
    目的のページに遷移する。
    """
    #    print('Navigating...', file=sys.stderr)
    # driver.get('https://note.mu/hashtag/箕輪編集室?f=popular')  # noteのトップページを開く。
    driver.get('https://note.mu/search?context=note&q=箕輪編集室・公式&mode=search')  # noteのトップページを開く。

    sleep(1)

    assert 'note' in driver.title  # タイトルに'note'が含まれていることを確認する。


def scrape_posts(driver):
    """
    文章コンテンツのURL、タイトル、概要を含むdictのリストを取得する。
    """
    posts = []

    # すべての文章コンテンツを表すa要素について反復する。
    for h3 in driver.find_elements_by_xpath("//h3[@class='renewal-p-cardItem__title']"):
        # URL、タイトル、概要を取得して、dictとしてリストに追加する。
        posts.append({
            'title': h3.find_element_by_css_selector('a').text,
            'url': h3.find_element_by_css_selector('a').get_attribute('href'),
        })
    
    return posts

if __name__ == '__main__':
    main()
