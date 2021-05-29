import requests
import discord
import json
import time
import datetime

TIME_LIMIT = 60*60+2
from .constants import REMINDER_CHANNELS
id_to_platform= {
    2:'Codechef',
    1:'Codeforces',
    93:'Atcoder',
    102: 'Leetcode',
    35: 'Google',
    73: 'Hackerearth',
    123: 'Codedrills',
    12:'Topcoder',
    117:'BinarySearch'
}



def get_formatted_contest_desc(id_str, start, duration, url, max_duration_len):
    em = '\N{EN SPACE}'
    sq = '\N{WHITE SQUARE WITH UPPER RIGHT QUADRANT}'
    desc = (f'`{em}{id_str}{em}| {em}{start}{em}| {em}{duration.rjust(max_duration_len, em)}{em}|' f'{em}`[`link {sq}`]({url} "Link to contest page")')
    return desc


def getFutureContest(res,platform):
	desc = f"**About to start in 1 hour <@&{REMINDER_CHANNELS[platform+'_Role']}> **"
	embed = discord.Embed(description=desc, color=discord.Colour.gold())

	if len(res)==0:
		return None
	
	def convert(seconds): 
		seconds = seconds % (24 * 3600) 
		hour = seconds // 3600
		seconds %= 3600
		minutes = seconds // 60
		seconds %= 60
		return "%d:%02d" % (hour, minutes) 

	for i in range(len(res)):
		con = res[i]
		duration = convert(int(con[1]))
		name = con[0]
		url = con[3]
		start = con[2].replace("T"," ")
		em = '\N{EN SPACE}'
		sq = '\N{WHITE SQUARE WITH UPPER RIGHT QUADRANT}'
		desc = (f'`{em}{start}{em}| {em}{duration.rjust(5, em)}{em}| {em}`[`link {sq}`]({url} "Link to contest page")')
		embed.add_field(name=f"{name}", value= desc  ,inline=False)
	return embed



def getNextContest():
    current_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
	
    url = f"https://clist.by/api/v1/contest/?start__gt={current_time}&order_by=start"
    headers = {
        'Authorization': 'ApiKey btech15060.18:534ebe6eb3d4e07ca265ca963bf2a32658efe530'
    }
    data = json.loads(requests.get(url, headers=headers).content)['objects']
    return data

def getRecentContests():
    all_contests = getNextContest()
    res = {}
    for data in all_contests:
        name = data['event']
        platform = data['resource']['id']
        start_time = data['start']
        link = data['href']
        dur = data['duration']
        time_left = int(datetime.datetime.timestamp(datetime.datetime.strptime(start_time,'%Y-%m-%dT%H:%M:%S')))
        cur_time = datetime.datetime.timestamp(datetime.datetime.utcnow())
        time_left= int(time_left-cur_time)
        if time_left <= TIME_LIMIT and platform in id_to_platform.keys():
            if id_to_platform[platform] in res.keys():
                res[id_to_platform[platform]].append([name,dur,start_time,link])
            else:
                res[id_to_platform[platform]]=list()
                res[id_to_platform[platform]].append([name,dur,start_time,link])
    return res

def scale_username(a,ln):
	a=str(a)
	while(len(a)<ln):
		a=a+" "
	longer = False
	if len(a)>ln:
		longer = True
	while len(a)>ln:
		a = a[:-1]
	if longer:
		a = a[:-3]
		a += "..."
	return a

def getRecentContestsAll():
    all_contests = getNextContest()
    res = []
    for data in all_contests:
        name = data['event']
        platform = data['resource']['id']
        start_time = data['start']
        link = data['href']
        dur = data['duration']
        time_left = int(datetime.datetime.timestamp(datetime.datetime.strptime(start_time,'%Y-%m-%dT%H:%M:%S')))
        cur_time = datetime.datetime.timestamp(datetime.datetime.utcnow())
        time_left= int(time_left-cur_time)
        if platform in id_to_platform.keys() and platform!=73:
            res.append([scale_username(name,20),dur,time_left,id_to_platform[platform]])
    return res