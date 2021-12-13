# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TutorialItem(scrapy.Item):
    # define the fields for your item here like:
        timestamp = scrapy.Field()
        server = scrapy.Field()
        #mmr = scrapy.Field()
        result = scrapy.Field()
        team_1 = scrapy.Field()
        team_2 = scrapy.Field()
       # t1_recent_winrates = scrapy.Field()
        #t2_recent_winrates = scrapy.Field()
        #t1_overall_winrates = scrapy.Field()
        #t2_overall_winrates = scrapy.Field()
        #t1_wlrecord = scrapy.Field()
        #t2_wlrecord = scrapy.Field()
        # players_1=scrapy.Field()
        # players_2=scrapy.Field()



