from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import copy
from slacker import Slacker
import websockets
import json 
import asyncio

def getSteamAppId(gameName):
    req_url = "https://steamdb.info/search/?a=app&q=" + gameName +"&type=1&category=0"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    req = Request(url = req_url, headers = headers)
    soup = BeautifulSoup(urlopen(req).read(), "html.parser")
    steamAppId = soup.find('tbody').find('tr').find('a').get_text()
    print(steamAppId)
    return steamAppId

def getSteamReviews(gameAppId):
    req_url = "https://store.steampowered.com/app/" + gameAppId

    soup = BeautifulSoup(urlopen(req_url).read(), "html.parser")
    steamUsersReviews = soup.find('div',class_='summary column').find('span').get_text()
    print(steamUsersReviews)
    if 'Positive' in steamUsersReviews:
        return '좋음'
    elif 'Mixed' in steamUsersReviews:
        return '애매함'
    else :
        return '똥겜'

async def execute_bot():
        
    token = 'xoxb-507380538243-507690072389-qoKlkzFOxIhzJftBsAKabE8q'
    slack = Slacker(token)
    response = slack.rtm.connect()
    sock_endpoint = response.body['url']
    slack_socket = await websockets.connect(sock_endpoint)
    while True:
        msg = await slack_socket.recv()
        msg = json.loads(msg)
        print(msg)
        if 'text' in msg.keys() and 'bot_id' not in msg.keys():
            if '스팀에서' in msg['text']:
                gameName = msg['text'].replace('스팀에서','').strip().split()[0]
                steamAppId = getSteamAppId(gameName)
                message = getSteamReviews(steamAppId)
                slack.chat.post_message(msg['channel'], message)
            else :
                slack.chat.post_message(msg['channel'],msg['text'])



loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
asyncio.get_event_loop().run_until_complete(execute_bot())
asyncio.get_event_loop().run_forever()
