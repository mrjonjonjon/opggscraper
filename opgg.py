
# -*- coding: utf-8 -*-
import ast
import time
import re
def stripslashes(s):
    r = re.sub(r"\\(n|r)", "\n", s)
    r = re.sub(r"\\", "", r)
    return r

import scrapy
from scrapy import Request

from ..constants import XPATHS_LADDER, XPATHS_GAME
from inline_requests import inline_requests

from ..items import TutorialItem

timestamps=set()
count=0
total=0
class OpggSpider(scrapy.Spider):
    name = 'opgg'
    allowed_domains = ['op.gg']
    #servers = ['br', 'jp', 'www','euw', 'oce', 'lan', 'tr', 'na', 'eune', 'las', 'ru']
    servers=['na']
    start_urls = ['https://na.op.gg/summoner/userName=xxquakeroatsxx']
    #start_urls=['https://ru.op.gg/summoner/userName=%D0%9F%D0%90%D0%92%D0%9B%D0%AF%D0%94%D0%98%D0%9A%D0%98%D0%99%D0%9F%D0%81%D0%A1666']

    #@inline_requests
    def parse(self, response):
       # print('response is',response.body)

        count=0
        total=0
        matches = response.xpath(XPATHS_GAME['_matches'])
        for i,match in enumerate(matches):
            print('x',i)
            summoners_t1 = match.xpath(XPATHS_GAME['_summoners_team_1'])
            summoners_t2 = match.xpath(XPATHS_GAME['_summoners_team_2'])
            #print('mmm',summoners_t1)
            #if not response.meta.get('related'):
            #    self._parse_profile_links(summoners_t1)
            #    self._parse_profile_links(summoners_t2)

            match_type = match.xpath(XPATHS_GAME['_match_type']).extract_first().strip()
            #print('aaa',match_type)
            result = match.xpath(XPATHS_GAME['result']).extract_first().strip()
            #if match_type != 'Ranked Solo' or result == 'Remake':
                #continue

            selector_t1 = match.xpath(XPATHS_GAME['_champions_team_1'])
            selector_t2 = match.xpath(XPATHS_GAME['_champions_team_2'])
            team_1 = list(selector_t1.xpath('.//div[1]//text()').extract())
            team_2 = list(selector_t2.xpath('.//div[1]//text()').extract())
            #print('t1',team_1)
            item = TutorialItem()
            #result = response.xpath(XPATHS_GAME['result']).extract_first().strip()
            player = response.xpath(XPATHS_GAME['player']).extract_first()
            players_t1 = [summoner.xpath('.//text()').extract()[1] for summoner in summoners_t1]
            players_t2= [summoner.xpath('.//text()').extract()[1] for summoner in summoners_t2]
            #print(result,players_t1)
            if player in players_t1:
                if result == 'Victory':
                    item['result'] = 'Victory'
                    #print('v1')
                else:
                    item['result'] = 'Defeat'
                    #print('v2')
            else:
                if result == 'Victory':
                    item['result'] = 'Defeat'
                    #print('v3')
                else:
                    item['result'] = 'Victory'
                    #print('v4')

            if ('Master Yi' in team_1 and player in team_1 ) or ('Master Yi' in team_2 and player in team_2):
                count+=1
                total+=1
            #print('tt',team_1 if player in team_1 else team_2)
            #item['server'] = response.url.split('/')[2].split('.')[0]
           # item['mmr'] = response.xpath(XPATHS_GAME['mmr']).extract_first()
            item['team_1'] = team_1
            item['team_2'] = team_2
            #item['players_1']=players_t1
            #item['players_2']=players_t2
            item['timestamp'] = match.xpath(XPATHS_GAME['timestamp']).extract_first()
            if item['timestamp'] in timestamps:
                continue
            print(team_1,team_2,item['result'])
            timestamps.add(item['timestamp'])

            allwrs1=[]
            #item['t1_recent_winrates']=[]
            #item['t2_recent_winrates']=[]
            #item['t1_overall_winrates']=[]
            #item['t2_overall_winrates']=[]


            #item['t1_wlrecord']=[]
            #item['t2_wlrecord']=[]


            # yield item

            yield item
        num=response.xpath('.//div[@class="GameListContainer"]/@data-last-info').extract_first()

        print('num is',num,type(num))
        yield Request(
                'https://na.op.gg/summoner/matches/ajax/averageAndList/startInfo='+num+'&summonerId=91392613',
                callback=self.parse2)

    def parse2(self, response):
        #print('response is',response.body)
        #print(ast.literal_eval(response.text)['html'])

        num=str(ast.literal_eval(response.text)['lastInfo'])
        response=response.replace(body=stripslashes(ast.literal_eval(response.text)['html']))

        #response=response['html']

        count = 0
        total = 0
        matches = response.xpath(XPATHS_GAME['_matches'])
        #print('matches',response.text)
        for i, match in enumerate(matches):
            print('x', i)
            summoners_t1 = match.xpath(XPATHS_GAME['_summoners_team_1'])
            summoners_t2 = match.xpath(XPATHS_GAME['_summoners_team_2'])
            # print('mmm',summoners_t1)
            # if not response.meta.get('related'):
            #    self._parse_profile_links(summoners_t1)
            #    self._parse_profile_links(summoners_t2)

            match_type = match.xpath(XPATHS_GAME['_match_type']).extract_first().strip()
            # print('aaa',match_type)
            result = match.xpath(XPATHS_GAME['result']).extract_first().strip()
            # if match_type != 'Ranked Solo' or result == 'Remake':
            # continue

            selector_t1 = match.xpath(XPATHS_GAME['_champions_team_1'])
            selector_t2 = match.xpath(XPATHS_GAME['_champions_team_2'])
            team_1 = list(selector_t1.xpath('.//div[1]//text()').extract())
            team_2 = list(selector_t2.xpath('.//div[1]//text()').extract())
            # print('t1',team_1)
            item = TutorialItem()
            # result = response.xpath(XPATHS_GAME['result']).extract_first().strip()
            player = 'XxQuakerOatsxX'
            players_t1 = [summoner.xpath('.//text()').extract()[1] for summoner in summoners_t1]
            players_t2 = [summoner.xpath('.//text()').extract()[1] for summoner in summoners_t2]
            # print(result,players_t1)
            if player in players_t1:
                if result == 'Victory':
                    item['result'] = 'Victory'
                    # print('v1')
                else:
                    item['result'] = 'Defeat'
                    # print('v2')
            else:
                if result == 'Victory':
                    item['result'] = 'Defeat'
                    # print('v3')
                else:
                    item['result'] = 'Victory'
                    # print('v4')

            if ('Master Yi' in team_1 and player in team_1) or ('Master Yi' in team_2 and player in team_2):
                count += 1
                total += 1
            # print('tt',team_1 if player in team_1 else team_2)
            # item['server'] = response.url.split('/')[2].split('.')[0]
            # item['mmr'] = response.xpath(XPATHS_GAME['mmr']).extract_first()
            item['team_1'] = team_1
            item['team_2'] = team_2
            # item['players_1']=players_t1
            # item['players_2']=players_t2
            item['timestamp'] = match.xpath(XPATHS_GAME['timestamp']).extract_first()
            if item['timestamp'] in timestamps:
                continue
            #print(team_1, team_2, item['result'])
            timestamps.add(item['timestamp'])

            allwrs1 = []
            # item['t1_recent_winrates']=[]
            # item['t2_recent_winrates']=[]
            # item['t1_overall_winrates']=[]
            # item['t2_overall_winrates']=[]

            # item['t1_wlrecord']=[]
            # item['t2_wlrecord']=[]

            # yield item

            yield item


        print('num is', num, type(num))
        yield Request('https://na.op.gg/summoner/matches/ajax/averageAndList/startInfo=' + num + '&summonerId=91392613',callback=self.parse2)