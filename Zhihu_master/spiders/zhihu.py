# -*- coding: utf-8 -*-
import json
from scrapy import Request, Spider
from Zhihu_master.items import UserItem


class ZhihuSpider(Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    start_user = 'excited-vczh'
    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    user_query = 'allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,articles_count,gender,badge[?(type=best_answerer)].topics'

    followees_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    followees_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    followers_url = 'https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset={offset}&limit={limit}'
    followers_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    def start_requests(self):
        yield Request(url=self.user_url.format(user=self.start_user, include=self.user_query), callback=self.user_paser)
        yield Request(url=self.followees_url.format(user=self.start_user, include=self.followees_query, offset=0, limit=20), callback=self.followees_paser)
        yield Request(url=self.followers_url.format(user=self.start_user, include=self.followers_query, offset=0, limit=20), callback=self.followers_paser)

    def user_paser(self, response):
        results = json.loads(response.text)
        items = UserItem()
        for field in items.fields:
            if field in results.keys():
                items[field] = results.get(field)
        yield items

    def followees_paser(self, response):
        results = json.loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data'):
                yield Request(url=self.user_url.format(user=result.get('url_token'), include=self.user_query),
                              callback=self.user_paser)
        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
                yield Request(url=results.get('paging').get('next'), callback=self.followees_paser)

    def followers_paser(self, response):
        results = json.loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data'):
                yield Request(url=self.user_url.format(user=result.get('url_token'), include=self.user_query),
                              callback=self.user_paser)
        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
                yield Request(url=results.get('paging').get('next'), callback=self.followers_paser)

