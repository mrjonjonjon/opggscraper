
# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import ast
from collections import defaultdict
import time
import re

import numpy as np
from scrapy import Request
from urllib.parse import quote_plus
import scrapy
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
def getkda(s):
    if s=='Perfect':
        return 5.0
    ans = re.search('([0-9]*[.][0-9]*):([0-9]*)', s, re.IGNORECASE)
    if ans:
        return float(ans.group(1))
def stripslashes(s):
    r = re.sub(r"\\(n|r)", "\n", s)
    r = re.sub(r"\\", "", r)
    return r
XPATHS_GAME = {
    'mmr': '//div[@class="TierRank"]/text()',
    'result': './/div[@class="GameResult"]/text()',
    '_match_type': './/div[@class="GameType"]/text()',
    '_matches': '//div[@class="GameItemWrap"]',
    '_champions_team_1': './/div[@class="Team"][1]//div[@class="ChampionImage"]',
    '_champions_team_2': './/div[@class="Team"][2]//div[@class="ChampionImage"]',
    '_summoners_team_1': './/div[@class="Team"][1]//div[@class="SummonerName"]',
    '_summoners_team_2': './/div[@class="Team"][2]//div[@class="SummonerName"]',
    '_champion_name': './/div/text()',
    'timestamp': './/div[@class="TimeStamp"]//span/text()',
    'profile_link': './/a/@href',
    'player': '//div[@class="Information"]/span//text()'
}
XPATHS_LADDER = {
    '_summoners': '//a[not(contains(@class, "ranking-highest__name"))]//@href[contains(.,"userName")]'
}


class TutorialItem(scrapy.Item):

        timestamp = scrapy.Field()
        server = scrapy.Field()
        #mmr = scrapy.Field()
        result = scrapy.Field()
        team_1 = scrapy.Field()
        team_2 = scrapy.Field()



#from ..constants import XPATHS_LADDER, XPATHS_GAME
from inline_requests import inline_requests

#from ..items import TutorialItem

timestamps=set()

class OpggSpider(scrapy.Spider):
    handle_httpstatus_list = [418]

    name = 'opgg'
    allowed_domains = ['op.gg']
    servers=['na']
    count=0
    yiwins=0
    topkda=0
    otherkda=0

    alldists=defaultdict(list)
    def start_requests(self):
        yield scrapy.Request('https://na.op.gg/summoner/userName=' + quote_plus(p1) )

    def closed(self, reason):
        print('topkda',self.topkda,self.count)
        print('otherkda',self.otherkda,self.count*4)
        for i in ['top','jg','mid','adc','sup']:
            n, bins, patches = plt.hist(self.alldists[i],bins=np.arange(0,30, 0.5))
            plt.savefig(f'{i}.pdf')


    def getstats(self,response):
        kdas=response.xpath('.//span[contains(@class,"KDARatio")]/text()').extract()
        t1_kdas=kdas[0:5]
        t2_kdas=kdas[5:]
        print('kdas are:',t1_kdas,t2_kdas)
        self.topkda+=getkda(t1_kdas[0])
        self.alldists['top'].append(getkda(t1_kdas[0]))
        self.alldists['top'].append(getkda(t2_kdas[0]))
        self.alldists['jg'].append(getkda(t1_kdas[1]))
        self.alldists['jg'].append(getkda(t2_kdas[1]))
        self.alldists['mid'].append(getkda(t1_kdas[2]))
        self.alldists['mid'].append(getkda(t2_kdas[2]))
        self.alldists['adc'].append(getkda(t1_kdas[3]))
        self.alldists['adc'].append(getkda(t2_kdas[3]))
        self.alldists['sup'].append(getkda(t1_kdas[4]))
        self.alldists['sup'].append(getkda(t2_kdas[4]))


        self.otherkda+=sum([getkda(t1_kdas[i]) for i in range(1,5)])
        print('sample',getkda(t1_kdas[0]))

    def parse(self, response):
        matches = response.xpath(XPATHS_GAME['_matches'])
        for i,match in enumerate(matches):
            summoners_t1 = match.xpath(XPATHS_GAME['_summoners_team_1'])
            summoners_t2 = match.xpath(XPATHS_GAME['_summoners_team_2'])
            match_type = match.xpath(XPATHS_GAME['_match_type']).extract_first().strip()
            result = match.xpath(XPATHS_GAME['result']).extract_first().strip()

            if match_type != 'Ranked Solo' or result == 'Remake':
                continue

            selector_t1 = match.xpath(XPATHS_GAME['_champions_team_1'])
            selector_t2 = match.xpath(XPATHS_GAME['_champions_team_2'])
            team_1 = list(selector_t1.xpath('.//div[1]//text()').extract())
            team_2 = list(selector_t2.xpath('.//div[1]//text()').extract())

            item = TutorialItem()
            player = response.xpath(XPATHS_GAME['player']).extract_first()
            players_t1 = [summoner.xpath('.//text()').extract()[1] for summoner in summoners_t1]
            players_t2 = [summoner.xpath('.//text()').extract()[1] for summoner in summoners_t2]

            if player in players_t1:
                if result == 'Victory':
                    item['result'] = 'Victory'
                else:
                    item['result'] = 'Defeat'
            else:
                if result == 'Victory':
                    item['result'] = 'Defeat'
                else:
                    item['result'] = 'Victory'


            if self.p2 in players_t2 or self.p2 in players_t1:
                print(players_t1,players_t2)

            if ('Master Yi' in team_1 and player in players_t1) or ('Master Yi' in team_2 and player in players_t2):
                #self.count += 1
                self.yiwins += 1 if ((result == 'Victory' and player in players_t1) or (result == 'Defeat' and player in players_t2)) else 0
            self.count += 1

            item['team_1'] = team_1
            item['team_2'] = team_2
            item['timestamp'] = match.xpath(XPATHS_GAME['timestamp']).extract_first()
            if item['timestamp'] in timestamps:
                continue

            timestamps.add(item['timestamp'])

            gameid=match.xpath('./div[1]/@data-game-id').extract_first()
            summonerid=match.xpath('./div[1]/@data-summoner-id').extract_first()
            gametime=match.xpath('./div[1]/@data-game-time').extract_first()
            #print(gameid,summonerid,gametime)

           # yield Request('https://na.op.gg/summoner/matches/ajax/detail/gameId='+gameid+'&summonerId='+summonerid+'&gameTime='+gametime,callback=self.getstats)
            yield item
        num=response.xpath('.//div[@class="GameListContainer"]/@data-last-info').extract_first()

        yield Request('https://na.op.gg/summoner/matches/ajax/averageAndList/startInfo='+num+'&summonerId=91392613',callback=self.parse2)

    def parse2(self, response):
        if response.status==418:
            print('done',self.count)
            return
        num=str(ast.literal_eval(response.text)['lastInfo'])
        response=response.replace(body=stripslashes(ast.literal_eval(response.text)['html']))
        matches = response.xpath(XPATHS_GAME['_matches'])

        for i, match in enumerate(matches):
            summoners_t1 = match.xpath(XPATHS_GAME['_summoners_team_1'])
            summoners_t2 = match.xpath(XPATHS_GAME['_summoners_team_2'])
            match_type = match.xpath(XPATHS_GAME['_match_type']).extract_first().strip()
            result = match.xpath(XPATHS_GAME['result']).extract_first().strip()
            #if match_type != 'Ranked Solo' or result == 'Remake':
            #  continue

            selector_t1 = match.xpath(XPATHS_GAME['_champions_team_1'])
            selector_t2 = match.xpath(XPATHS_GAME['_champions_team_2'])
            team_1 = list(selector_t1.xpath('.//div[1]//text()').extract())
            team_2 = list(selector_t2.xpath('.//div[1]//text()').extract())
            item = TutorialItem()
            player = self.p1
            players_t1 = [summoner.xpath('.//text()').extract()[1] for summoner in summoners_t1]
            players_t2 = [summoner.xpath('.//text()').extract()[1] for summoner in summoners_t2]
            if self.p2 in players_t2 or self.p2 in players_t1:
                print(players_t1, players_t2)

            # print(result,players_t1)
            if player in players_t1:
                if result == 'Victory':
                    item['result'] = 'Victory'

                else:
                    item['result'] = 'Defeat'

            else:
                if result == 'Victory':
                    item['result'] = 'Defeat'

                else:
                    item['result'] = 'Victory'


            if ('Master Yi' in team_1 and player in players_t1) or ('Master Yi' in team_2 and player in players_t2):
                #self.count += 1
                self.yiwins += 1 if ((result=='Victory' and player in players_t1) or (result=='Defeat' and player in players_t2)) else 0
            self.count += 1


            item['team_1'] = team_1
            item['team_2'] = team_2

            item['timestamp'] = match.xpath(XPATHS_GAME['timestamp']).extract_first()
            if item['timestamp'] in timestamps:
                continue
            #print(team_1, team_2, item['result'])
            timestamps.add(item['timestamp'])
            gameid = match.xpath('./div[1]/@data-game-id').extract_first()
            summonerid = match.xpath('./div[1]/@data-summoner-id').extract_first()
            gametime = match.xpath('./div[1]/@data-game-time').extract_first()
            #print(gameid, summonerid, gametime)

            #yield Request('https://na.op.gg/summoner/matches/ajax/detail/gameId=' + gameid + '&summonerId=' + summonerid + '&gameTime=' + gametime,callback=self.getstats)
            yield item


        
        yield Request('https://na.op.gg/summoner/matches/ajax/averageAndList/startInfo=' + num + '&summonerId=91392613',callback=self.parse2)


if __name__ ==  "__main__":
    type=input('Enter query type:')
    p1 = input("Enter p1:")
    p2 = input('Enter p2:')
    process = CrawlerProcess(get_project_settings())
    process.crawl(OpggSpider,p1=p1,p2=p2)
    process.start()
