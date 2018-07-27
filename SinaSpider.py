#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 20 16:40:01 2018

@author: xuzhiwei
"""

import re
import requests
import json
import pandas
from bs4 import BeautifulSoup


def getNewsDetail(newsurl):
    result = {}
    res = requests.get(newsurl)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    result['title'] = soup.select('.main-title')[0].text  # 标题
    result['dt'] = soup.select('.date')[0].contents[0]  # 时间
    result['newssoure'] = soup.select('.date-source a')[0].text  # 来源
    result['article'] = '\n'.join(p.text.strip()
                                  for p in soup.select('#article p')[:-1])  # 内容
    result['author'] = soup.select('.show_author')[
        0].text.lstrip('责任编辑：').rstrip()  # 作者
    result['comments'] = getCommentCounts(newsurl)

    return result


def getCommentCounts(newsurl):
    commetURL = 'http://comment5.news.sina.com.cn/page/info?version=1\
    &format=json&channel=gn&newsid=comos-{}&group=undefined&compress=0\
    &ie=utf-8&oe=utf-8&page=1&page_size=3&t_size=3&h_size=3&thread=1'
    m = re.search('doc-i(.*).shtml', newsurl)
    newsid = m.group(1)
    comments = requests.get(commetURL.format(newsid))
    jd = json.loads(comments.text)

    return jd['result']['count']['total']


def parseListLinks(url):
    newsdetails = []
    res = requests.get(url)
    jd = json.loads(res.text.lstrip('  newsloadercallback(').rstrip(');'))
    for ent in jd['result']['data']:
        newsdetails.append(getNewsDetail(ent['url']))
    return newsdetails

url = 'http://api.roll.news.sina.com.cn/zt_list?channel=news\
    &cat_1=gnxw&cat_2==gdxw1||=gatxw||=zs-pl||=mtjj&level==1||=2\
    &show_ext=1&show_all=1&show_num=22&tag=1&format=json&page={}'

news_total = []
for i in range(2, 3):
    newsurl = url.format(i)
    newsary = parseListLinks(newsurl)
    news_total.extend(newsary)

df = pandas.DataFrame(news_total)

df.to_excel('news.xlsx')  # 存储到Excel
